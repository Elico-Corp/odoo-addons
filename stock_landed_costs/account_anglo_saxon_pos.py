# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, osv, fields
import time
from openerp.tools.translate import _


class pos_order(orm.Model):
    _inherit = 'pos.order'

    def _create_account_move_line(self, cr, uid, ids, session=None, move_id=None, context=None):
        # Tricky, via the workflow, we only have one id in the ids variable
        """Create a account move line of order grouped by products or not.

        Fully inherit this method and get the right cost price."""
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_period_obj = self.pool.get('account.period')
        account_tax_obj = self.pool.get('account.tax')
        user_proxy = self.pool.get('res.users')
        property_obj = self.pool.get('ir.property')

        period = account_period_obj.find(cr, uid, context=context)[0]

        #session_ids = set(order.session_id for order in self.browse(cr, uid, ids, context=context))

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
            shop_id = order.shop_id
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

                # 'quantity': line.qty,
                # 'product_id': line.product_id.id,
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
                    key = ('anglo', values['partner_id'], values['product_id'], values['account_id'], values['debit'] > 0)
                else:
                    return

                if not grouped_data.get(key, False):
                    grouped_data.setdefault(key, [])

                # if not have_to_group_by or (not grouped_data[key]):
                #     grouped_data[key].append(values)
                # else:
                #     pass

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
                    # change begin. get the right cost price.
                    if line.company_id.support_duty_zone and shop_id:
                        location_id = shop_id.warehouse_id.lot_stock_id
                        price_name = location_id and location_id.duty_zone_id.price_type_id.field\
                            or 'standard_price'
                        amount = getattr(line.product_id, price_name) * line.qty
                    else:
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

            order.write({'state': 'done', 'account_move': move_id})
        for group_key, group_data in grouped_data.iteritems():
            for value in group_data:
                account_move_line_obj.create(cr, uid, value, context=context)

        return True


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def get_price_unit(self, cr, uid, company_currency, i_line):
        # get the invoice
        assert i_line.invoice_id, 'There is no invoice for the invoice line!'
        invoice = i_line.invoice_id
        price = 0.0
        cur_obj = self.pool.get('res.currency')
        decimal_precision = self.pool.get('decimal.precision')

        # get proper cost price for duty-zone-supported company
        # for customer invoice and customer refund, we all have the sale id linked.
        if invoice.company_id.support_duty_zone:
            if invoice.sale_ids:
                # get the first sale order of invoice
                sale = invoice.sale_ids and invoice.sale_ids[0] or None
                if sale:
                    location_id = sale.shop_id.warehouse_id.lot_stock_id
                    if not location_id.duty_zone_id:
                        raise osv.except_osv(
                            ('Warning'),
                            ('Please set the duty '
                                'zone for the location: %s !' % location_id.complete_name))
                    price_name = location_id.duty_zone_id.price_type_id.field
                    price = getattr(i_line.product_id, price_name)
        else:
            price = i_line.product_id.standard_price
        if invoice.currency_id.id != company_currency:
            price = cur_obj.compute(
                cr, uid, company_currency, invoice.currency_id.id,
                price,
                context={'date': invoice.date_invoice})
        return round(price, decimal_precision.precision_get(cr, uid, 'Account'))

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id

        # add if not to remove Ios line
        # task 5732 by chen.rong
        if not inv.not_generate_line:
            for line in inv.invoice_line:
                mres = self.move_line_get_item(cr, uid, line, context)
                mres['invl_id'] = line.id
                res.append(mres)
                tax_code_found= False
                for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
                        (line.price_unit * (1.0 - (line['discount'] or 0.0) / 100.0)),
                        line.quantity, line.product_id,
                        inv.partner_id)['taxes']:

                    if inv.type in ('out_invoice', 'in_invoice'):
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']

                    if tax_code_found:
                        if not tax_code_id:
                            continue
                        res.append(self.move_line_get_item(cr, uid, line, context))
                        res[-1]['price'] = 0.0
                        res[-1]['account_analytic_id'] = False
                    elif not tax_code_id:
                        continue
                    tax_code_found = True

                    res[-1]['tax_code_id'] = tax_code_id
                    res[-1]['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, tax_amount, context={'date': inv.date_invoice})
        # inherit from anglo saxon
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        company_currency = inv.company_id.currency_id.id
        
        def get_price(cr, uid, inv, company_currency, i_line):
            '''rewrite this function to get right cost price.
            :param type: incoming and outgoing
            '''
            # get the invoice
            assert i_line.invoice_id, 'There is no invoice for the invoice line!'
            price = 0.0
            decimal_precision = self.pool.get('decimal.precision')

            price = self.get_price_unit(cr, uid, company_currency, i_line)
            return round(
                price * i_line.quantity, decimal_precision.precision_get(cr, uid, 'Account'))
        
        # we get the proper cost price and accounts for duty zone supported company.
        if inv.type in ('out_invoice', 'out_refund'):
            for i_line in inv.invoice_line:
                if i_line.product_id and i_line.product_id.valuation == 'real_time':
                    if inv.type in ('out_invoice', 'out_refund'):
                        # debit account dacc will be the output account
                        # first check the product, if empty check the category
                        # Note: we use the stock output account for all customer related.
                        # include the refund from customer;
                        dacc = i_line.product_id.property_stock_account_output and \
                            i_line.product_id.property_stock_account_output.id
                        if not dacc:
                            dacc = i_line.product_id.categ_id.property_stock_account_output_categ\
                                and i_line.product_id.categ_id.property_stock_account_output_categ.id
                    # else:
                    #     # = out_refund
                    #     # debit account dacc will be the input account
                    #     # first check the product, if empty check the category
                    #     dacc = i_line.product_id.property_stock_account_input\
                    #         and i_line.product_id.property_stock_account_input.id
                    #     if not dacc:
                    #         dacc = i_line.product_id.categ_id.property_stock_account_input_categ\
                    #             and i_line.product_id.categ_id.property_stock_account_input_categ.id
                    # in both cases the credit account cacc will be the expense account
                    # first check the product, if empty check the category
                    cacc = i_line.product_id.property_account_expense and i_line.product_id.property_account_expense.id
                    if not cacc:
                        cacc = i_line.product_id.categ_id.property_account_expense_categ and i_line.product_id.categ_id.property_account_expense_categ.id
                    if dacc and cacc:
                        res.append({
                            'type': 'src',
                            'name': i_line.name[:64],
                            'price_unit': i_line.product_id.standard_price,
                            'quantity': i_line.quantity,
                            'price': get_price(cr, uid, inv, company_currency, i_line),
                            'account_id': dacc,
                            'product_id': i_line.product_id.id,
                            'uos_id': i_line.uos_id.id,
                            'account_analytic_id': False,
                            'taxes': i_line.invoice_line_tax_id,
                        })

                        res.append({
                            'type': 'src',
                            'name': i_line.name[:64],
                            'price_unit': i_line.product_id.standard_price,
                            'quantity': i_line.quantity,
                            'price': -1 * get_price(cr, uid, inv, company_currency, i_line),
                            'account_id': cacc,
                            'product_id': i_line.product_id.id,
                            'uos_id': i_line.uos_id.id,
                            # 5191 add account_analytic
                            'account_analytic_id': i_line.account_analytic_id and i_line.account_analytic_id.id or False,
                            'taxes': i_line.invoice_line_tax_id,
                        })

        elif inv.type in ('in_invoice', 'in_refund'):
            for i_line in inv.invoice_line:
                if i_line.product_id and i_line.product_id.valuation == 'real_time':
                    if i_line.product_id.type != 'service':
                        # get the price difference account at the product
                        acc = i_line.product_id.property_account_creditor_price_difference and i_line.product_id.property_account_creditor_price_difference.id
                        if not acc:
                            # if not found on the product get the price difference account at the category
                            acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ and i_line.product_id.categ_id.property_account_creditor_price_difference_categ.id
                        a = None
                        if inv.type in ('in_invoice', 'in_refund'):
                            # oa will be the stock input account
                            # first check the product, if empty check the category
                            # Note: we use the stock input account for all the supplier releated invoices.
                            # include the supplier refund.
                            oa = i_line.product_id.property_stock_account_input and i_line.product_id.property_stock_account_input.id
                            if not oa:
                                oa = i_line.product_id.categ_id.property_stock_account_input_categ and i_line.product_id.categ_id.property_stock_account_input_categ.id
                        # else:
                        #     # = in_refund
                        #     # oa will be the stock output account
                        #     # first check the product, if empty check the category
                        #     oa = i_line.product_id.property_stock_account_output and i_line.product_id.property_stock_account_output.id
                        #     if not oa:
                        #         oa = i_line.product_id.categ_id.property_stock_account_output_categ and i_line.product_id.categ_id.property_stock_account_output_categ.id
                        if oa:
                            # get the fiscal position
                            fpos = i_line.invoice_id.fiscal_position or False
                            a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, oa)
                        diff_res = []
                        decimal_precision = self.pool.get('decimal.precision')
                        account_prec = decimal_precision.precision_get(cr, uid, 'Account')
                        # calculate and write down the possible price difference between invoice price and product price
                        for line in res:
                            if line.get('invl_id', 0) == i_line.id and a == line['account_id']:
                                uom = i_line.product_id.uos_id or i_line.product_id.uom_id
                                standard_price = self.pool.get('product.uom')._compute_price(
                                    cr, uid, uom.id, i_line.product_id.standard_price,
                                    i_line.uos_id.id)
                                if inv.currency_id.id != company_currency:
                                    standard_price = self.pool.get('res.currency').compute(cr, uid, company_currency, inv.currency_id.id, standard_price, context={'date': inv.date_invoice})
                                if standard_price != i_line.price_unit and line['price_unit'] == i_line.price_unit and acc:
                                    price_diff = round(i_line.price_unit - standard_price, account_prec)
                                    line.update({'price': round(standard_price * line['quantity'], account_prec)})
                                    diff_res.append({
                                        'type': 'src',
                                        'name': i_line.name[:64],
                                        'price_unit': price_diff,
                                        'quantity': line['quantity'],
                                        'price': round(price_diff * line['quantity'], account_prec),
                                        'account_id': acc,
                                        'product_id': line['product_id'],
                                        'uos_id': line['uos_id'],
                                        'account_analytic_id': line['account_analytic_id'],
                                        'taxes': line.get('taxes', []),
                                    })
                        res += diff_res
        return res
# remove AR and TAX move line 
#task 5732 by chen.rong
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
                    raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            not_generate_line = False
            if inv.not_generate_line and inv.type in ('out_invoice', 'out_refund'):
                not_generate_line = True
            if not not_generate_line:
                iml += ait_obj.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
            acc_id = inv.account_id.id

            name = inv['name'] or inv['supplier_invoice_number'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if not not_generate_line:
                if totlines:
                    res_amount_currency = total_currency
                    i = 0
                    ctx.update({'date': inv.date_invoice})
                    for t in totlines:
                        if inv.currency_id.id != company_currency:
                            amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                        else:
                            amount_currency = False

                        # last line add the diff
                        res_amount_currency -= amount_currency or 0
                        i += 1
                        if i == len(totlines):
                            amount_currency += res_amount_currency

                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': acc_id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency_p \
                                    and amount_currency or False,
                            'currency_id': diff_currency_p \
                                    and inv.currency_id.id or False,
                            'ref': ref,
                        })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': acc_id,
                        'date_maturity': inv.date_due or False,
                        'amount_currency': diff_currency_p \
                                and total_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref
                })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')

            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id

            ctx.update(invoice=inv)
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _description = "Picking List"

    def action_invoice_create(
        self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        '''Return ids of created invoices for the pickings'''
        '''correct the behavior from module: account_anglo_saxon'''
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id, group, type, context=context)
        # notes: for all the supplier related invoices, we should always use the stock input account for consistence.
        if type in ('in_refund', 'in_invoice'):
            for inv in self.pool.get('account.invoice').browse(cr, uid, res.values(), context=context):
                for ol in inv.invoice_line:
                    if ol.product_id:
                        oa = ol.product_id.property_stock_account_input and ol.product_id.property_stock_account_input.id
                        if not oa:
                            oa = ol.product_id.categ_id.property_stock_account_input_categ and ol.product_id.categ_id.property_stock_account_input_categ.id
                        if oa:
                            fpos = ol.invoice_id.fiscal_position or False
                            a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, oa)
                            self.pool.get('account.invoice.line').write(cr, uid, [ol.id], {'account_id': a})
        return res
