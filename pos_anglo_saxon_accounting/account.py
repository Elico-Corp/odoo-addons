# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
from openerp import netsvc


class pos_session(orm.Model):
    _inherit = "pos.session"

    def wkf_action_close(self, cr, uid, ids, context=None):
        # Close CashBox
        context = context or {}
        bsl = self.pool.get('account.bank.statement.line')
        for record in self.browse(cr, uid, ids, context=context):
            for st in record.statement_ids:

                if st.journal_id.type == 'bank':
                    st.write({'balance_end_real': st.balance_end})
                if abs(st.difference) > st.journal_id.amount_authorized_diff:
                    # The pos manager can close statements with maximums.
                    if not self.pool.get('ir.model.access').check_groups(
                            cr, uid, "point_of_sale.group_pos_manager"):
                        raise osv.except_osv(
                            _('Error!'),
                            _("Your ending balance is too different from the theorical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
                if st.difference and st.journal_id.cash_control:
                    if st.difference > 0.0:
                        name = _('Point of Sale Profit')
                        account_id = st.journal_id.profit_account_id.id
                    else:
                        account_id = st.journal_id.loss_account_id.id
                        name = _('Point of Sale Loss')
                    if not account_id:
                        raise osv.except_osv(
                            _('Error!'),
                            _("Please set your profit and loss accounts on your payment method '%s'. This will allow OpenERP to post the difference of %.2f in your ending balance. To close this session, you can update the 'Closing Cash Control' to avoid any difference.") % (st.journal_id.name, st.difference))
                    bsl.create(cr, uid, {
                        'statement_id': st.id,
                        'amount': st.difference,
                        'ref': record.name,
                        'name': name,
                        'account_id': account_id
                    }, context=context)
                # Here we don't validate the POS related bank statement.
        self._confirm_orders(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'closed'}, context=context)

    def _confirm_orders(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")

        for session in self.browse(cr, uid, ids, context=context):
            order_ids = [order.id for order in session.order_ids if order.state == 'paid']

            
            '''ISSUE 2666 add done state to avoid warning message by chen rong'''
            for order in session.order_ids:
                if order.state not in ('paid', 'invoiced','done'):
                    raise osv.except_osv(
                        _('Error!'),
                        _("You cannot confirm all orders of this session, because they have not the 'paid' status"))
        return True

class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    def button_confirm_bank_2(self, cr, uid, ids, context=None):
        self.button_confirm_bank(cr, uid, ids, context=context)
        wf_service = netsvc.LocalService("workflow")
        statement = self.browse(cr, uid, ids, context=context)
        statement_line_ids = statement[0].line_ids
        for line in statement_line_ids:
            if_validate = True
            if  line.pos_statement_id:
                for bline in line.pos_statement_id.statement_ids:
                    if bline.statement_id.state != 'confirm':
                        if_validate = False
                        break
                if  if_validate and line.pos_statement_id.state != 'done':
                    wf_service.trg_validate(uid, 'pos.order', line.pos_statement_id.id, 'done', cr)
        if statement[0].pos_session_id:
            all_statement = len(statement[0].pos_session_id.statement_ids)
            for s in statement[0].pos_session_id.statement_ids:
                if s.state == 'confirm':
                    all_statement = all_statement - 1
            if all_statement == 0:
                for porder in statement[0].pos_session_id.order_ids:
                    wf_service.trg_validate(uid, 'pos.order', porder.id, 'done', cr)
        return True

class pos_order(orm.Model):
    _inherit = 'pos.order'

    def _create_account_move_line(self, cr, uid, ids, session=None, move_id=None, context=None):
        # Tricky, via the workflow, we only have one id in the ids variable
        """Create a account move line of order grouped by products or not."""
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_period_obj = self.pool.get('account.period')
        account_tax_obj = self.pool.get('account.tax')
        user_proxy = self.pool.get('res.users')
        property_obj = self.pool.get('ir.property')

        period = account_period_obj.find(cr, uid, context=context)[0]


        if session and not all(session.id == order.session_id.id for order in self.browse(cr, uid, ids, context=context)):
            raise osv.except_osv(_('Error!'), _('Selected orders do not have the same session!'))

        current_company = user_proxy.browse(cr, uid, uid, context=context).company_id

        grouped_data = {}
        have_to_group_by = session and session.config_id.group_by or False

        def compute_tax(amount, tax, line):
            if amount > 0:
                tax_code_id = tax['base_code_id']
                tax_amount = line.price_subtotal * tax['base_sign']
            else:
                tax_code_id = tax['ref_base_code_id']
                tax_amount = line.price_subtotal * tax['ref_base_sign']

            return (tax_code_id, tax_amount,)

        for order in self.browse(cr, uid, ids, context=context):
            if order.account_move:
                continue
            if order.state != 'paid':
                continue

            user_company = user_proxy.browse(cr, order.user_id.id, order.user_id.id).company_id

            group_tax = {}
            account_def = property_obj.get(cr, uid, 'property_account_receivable', 'res.partner', context=context).id

            order_account = order.partner_id and \
                order.partner_id.property_account_receivable and \
                order.partner_id.property_account_receivable.id or \
                account_def or current_company.account_receivable.id

            if move_id is None:
                # Create an entry for the sale
                move_id = account_move_obj.create(cr, uid, {
                    'ref': order.name,
                    'journal_id': order.sale_journal.id,
                }, context=context)

            def insert_data(data_type, values):
                # if have_to_group_by:

                sale_journal_id = order.sale_journal.id

                values.update({
                    'date': order.date_order[:10],
                    'ref': order.name,
                    'journal_id': sale_journal_id,
                    'period_id': period,
                    'move_id': move_id,
                    'company_id': user_company and user_company.id or False,
                })

                if data_type == 'product':
                    key = ('product', values['partner_id'], values['product_id'], values['debit'] > 0)
                elif data_type == 'tax':
                    key = ('tax', values['partner_id'], values['tax_code_id'], values['debit'] > 0)
                elif data_type == 'counter_part':
                    key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
                elif data_type == 'anglo':
                    key = ('anglo', values['partner_id'], values['product_id'], values['account_id'])
                else:
                    return

                if not grouped_data.get(key, False):
                    grouped_data.setdefault(key, [])

                

                if have_to_group_by:
                    if not grouped_data[key]:
                        grouped_data[key].append(values)
                    else:
                        current_value = grouped_data[key][0]
                        current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity', 0.0)
                        current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
                        current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
                        current_value['tax_amount'] = current_value.get('tax_amount', 0.0) + values.get('tax_amount', 0.0)
                else:
                    grouped_data[key].append(values)

            # Create an move for each order line
            anal_def_obj = self.pool.get('account.analytic.default')
            default_analytic = anal_def_obj.account_get(cr, uid, order.shop_id.id, order.channel_id.id, context=context)
            for line in order.lines:
                tax_amount = 0
                taxes = [t for t in line.product_id.taxes_id]
                computed_taxes = account_tax_obj.compute_all(
                    cr, uid, taxes, line.price_unit * (100.0 - line.discount) / 100.0, line.qty)['taxes']

                for tax in computed_taxes:
                    tax_amount += round(tax['amount'], 2)
                    group_key = (tax['tax_code_id'], tax['base_code_id'], tax['account_collected_id'], tax['id'])

                    group_tax.setdefault(group_key, 0)
                    group_tax[group_key] += round(tax['amount'], 2)

                amount = line.price_subtotal

                # Search for the income account
                if line.product_id.property_account_income.id:
                    income_account = line.product_id.property_account_income.id
                elif line.product_id.categ_id.property_account_income_categ.id:
                    income_account = line.product_id.categ_id.property_account_income_categ.id
                else:
                    raise osv.except_osv(
                        _('Error!'),
                        _('Please define income '
                            'account for this product: "%s" (id:%d).')
                        % (line.product_id.name, line.product_id.id, ))

                # Empty the tax list as long as there is no tax code:
                tax_code_id = False
                tax_amount = 0
                while computed_taxes:
                    tax = computed_taxes.pop(0)
                    tax_code_id, tax_amount = compute_tax(amount, tax, line)

                    # If there is one we stop
                    if tax_code_id:
                        break

                # Create a move for the line
                insert_data('product', {
                    'name': line.product_id.name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
                    'account_id': income_account,
                    'credit': ((amount > 0) and amount) or 0.0,
                    'debit': ((amount < 0) and -amount) or 0.0,
                    'analytic_account_id': default_analytic and default_analytic.analytic_id and default_analytic.analytic_id.id or None,
                    'tax_code_id': tax_code_id,
                    'tax_amount': tax_amount,
                    'partner_id': order.partner_id and order.partner_id.id or False
                })

                # Create the expense account/ output/ input account move.
                # get the subtotal amount
                if line.product_id and line.product_id.valuation == 'real_time':
                    amount = line.product_id.standard_price * line.qty
                    # if the quantity of product is minus, means this is a returned pos order
                    if line.qty > 0:
                        #credit account cacc will be the output account
                        cacc = line.product_id.property_stock_account_output and \
                            line.product_id.property_stock_account_output.id
                        if not cacc:
                            cacc = line.product_id.categ_id.property_stock_account_output_categ and \
                                line.product_id.categ_id.property_stock_account_output_categ.id
                    elif line.qty < 0:
                        #credit account cacc will be the input account
                        cacc = line.product_id.property_stock_account_input and \
                            line.product_id.property_stock_account_input.id
                        if not cacc:
                            cacc = line.product_id.categ_id.property_stock_account_input_categ and \
                                line.product_id.categ_id.property_stock_account_input_categ.id
                    # in both cases, the debit account dacc will be the expense account
                    dacc = line.product_id.property_account_expense and \
                        line.product_id.property_account_expense.id
                    if not dacc:
                        dacc = line.product_id.categ_id.property_account_expense_categ and \
                            line.product_id.categ_id.property_account_expense_categ.id
                    if dacc and cacc:
                        insert_data('anglo', {
                            'name': line.product_id.name,
                            'quantity': line.qty,
                            'credit': ((amount > 0) and amount) or 0.0,
                            'debit': ((amount < 0) and -amount) or 0.0,
                            'account_id': cacc,
                            'product_id': line.product_id.id,
                            'partner_id': order.partner_id and order.partner_id.id or False
                        })

                        insert_data('anglo', {
                            'name': line.product_id.name,
                            'quantity': line.qty,
                            'credit': ((amount < 0) and -amount) or 0.0,
                            'debit': ((amount > 0) and amount) or 0.0,
                            'account_id': dacc,
                            'analytic_account_id': default_analytic and default_analytic.analytic_id and default_analytic.analytic_id.id or None,
                            'product_id': line.product_id.id,
                            'partner_id': order.partner_id and order.partner_id.id or False
                        })

                # For each remaining tax with a code, whe create a move line
                for tax in computed_taxes:
                    tax_code_id, tax_amount = compute_tax(amount, tax, line)
                    if not tax_code_id:
                        continue

                    insert_data('tax', {
                        'name': _('Tax'),
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'account_id': income_account,
                        'credit': 0.0,
                        'debit': 0.0,
                        'tax_code_id': tax_code_id,
                        'tax_amount': tax_amount,
                        'partner_id': order.partner_id and order.partner_id.id or False
                    })

            # Create a move for each tax group
            (tax_code_pos, base_code_pos, account_pos, tax_id) = (0, 1, 2, 3)

            for key, tax_amount in group_tax.items():
                tax = self.pool.get('account.tax').browse(cr, uid, key[tax_id], context=context)
                insert_data('tax', {
                    'name': _('Tax') + ' ' + tax.name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
            
                    'account_id': key[account_pos],
                    'credit': ((tax_amount > 0) and tax_amount) or 0.0,
                    'debit': ((tax_amount < 0) and -tax_amount) or 0.0,
                    'tax_code_id': key[tax_code_pos],
                    'tax_amount': tax_amount,
                    'partner_id': order.partner_id and order.partner_id.id or False
                })

            # counterpart
            insert_data('counter_part', {
                #order.name,
                'name': _("Trade Receivables"),
                'account_id': order_account,
                'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
                'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
                'partner_id': order.partner_id and order.partner_id.id or False
            })

            order.write({'account_move': move_id, 'state': 'done'})
        for group_key, group_data in grouped_data.iteritems():
            for value in group_data:
                account_move_line_obj.create(cr, uid, value, context=context)

        return True

    

class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    _columns = {
        'pos_session_id': fields.many2one('pos.session', 'POS Session'),
    }
class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def write(self, cr, uid, ids, vals, context=None):
        result = super(account_invoice, self).write(cr, uid, ids, vals, context)
        invoices = self.browse(cr, uid, ids, context=context)
        for invoice in invoices:
            if invoice.fapiao_required == True and invoice.move_id:
                invoice.move_id.write({'fapiao_required': True})
                for line in invoice.move_id.line_id:
                    line.write({'fapiao_required': True})
            elif invoice.fapiao_required == False and invoice.move_id:
                invoice.move_id.write({'fapiao_required': False})
                for line in invoice.move_id.line_id:
                    line.write({'fapiao_required': False})                
            if invoice.fapiao_required == True and invoice.payment_ids:
                for payment in invoice.payment_ids:
                    payment.write({'fapiao_required': True})
            elif invoice.fapiao_required == False and invoice.payment_ids:
                for payment in invoice.payment_ids:
                    payment.write({'fapiao_required': False})
        return result

class account_move(orm.Model):
    _inherit = 'account.move'

    _columns = {
        'fapiao_required': fields.boolean('Fapiao issued', readonly = True)
    }

class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'fapiao_required': fields.boolean('Fapiao issued', readonly = True)
    }
