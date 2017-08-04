# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields
from openerp.tools.translate import _

import time


class landed_cost_position_invoice(orm.TransientModel):

    """ To create invoice for stock move"""

    _inherit = 'landed.cost.position.invoice'
    _description = 'Landed Cost Position Make Invoice'

    def _get_journal_id(self, cr, uid, context=None):
        journal_obj = self.pool.get('account.journal')
        journal_type = 'purchase'
        vals = []

        journal_ids = journal_obj.search(
            cr, uid, [('type', '=', journal_type)], context=context)
        for journal in journal_obj.browse(cr, uid, journal_ids, context=context):
            selection_val = journal.id, journal.name
            if selection_val not in vals:
                vals.append(selection_val)
        return vals

    def get_journal(self, cr, uid, context=None):
        res = self._get_journal_id(cr, uid, context=context)
        if res:
            return res[0][0]
        return False

    _columns = {
        'group_by_supplier': fields.boolean('Group By Supplier'),
        'group_by_picking': fields.boolean('Group By Picking'),
        'journal_id': fields.selection(
            _get_journal_id, 'Destination Journal', required=True),
        'invoice_date': fields.date('Invoiced date'),

    }

    _defaults = {
        'journal_id': get_journal,
    }

    def _get_lc_group_by_currency(self, cr, uid, lc_ids, default_currency_id, context=None):
        '''get grouped lc by currency.
        :param lc_ids: the ids of LC.
        :param default_currency_id: the company's default currency id.
        :return: list: {currency1: [ids1], currenct2: [ids2]...}'''
        if not lc_ids:
            return {}
        else:
            res = {}
            lc_obj = self.pool.get('landed.cost.position')
            for lc in lc_obj.browse(cr, uid, lc_ids, context=context):
                # TODO: to be more simple.
                if not lc.currency_id and not res.get(default_currency_id):
                    res[default_currency_id] = []
                elif not res.get(lc.currency_id.id, False):
                    res[lc.currency_id.id] = []

                if lc.currency_id:
                    res[lc.currency_id.id].append(lc.id)
                else:
                    res[default_currency_id].append(lc.id)
            return res

    def make_invoices(self, cr, uid, ids, context=None):

        context = context or None
        record_ids = context.get('active_ids', [])
        invoice_ids = []
        wiz = self.browse(cr, uid, ids, context=context)[0]
        ctx = context.copy()
        ctx['group_by_supplier'] = wiz.group_by_supplier
        ctx['group_by_picking'] = wiz.group_by_picking
        ctx['invoice_date'] = wiz.invoice_date
        ctx['journal_id'] = wiz.journal_id and int(wiz.journal_id)
        #get default currency id
        user_obj = self.pool.get('res.users')
        default_currency_id = user_obj.browse(
            cr, uid, uid, context=context).company_id.currency_id.id
        assert default_currency_id

        # group by currency and create invoices accordingly.
        group_by_currency = self._get_lc_group_by_currency(
            cr, uid, record_ids, default_currency_id, context=context)
        # check if the currency generated properly.
        if group_by_currency:
            for record_ids in group_by_currency.values():
                invoice_ids.extend(self._generate_invoice_from_landed_cost(
                    cr, uid, record_ids, context=ctx))
        domain = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"
        return {
            'domain': domain,
            'name': _('Landed Cost Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
            'type': 'ir.actions.act_window'
        }

    def onchange_group_by_supplier(
            self, cr, uid, ids, group_by_supplier, context=None):
        '''when changing the group by supplier, we should change the group by supplier'''
        val = {}
        if not group_by_supplier:
            val['group_by_picking'] = False
        return {'value': val}

    #
    # create invoice for the landed costs
    #
    def _prepare_group_invoice(
            self, cr, uid, lc, invoice, invoices_group, context=None):
        '''
        :param lc: browse_record object of landed cost
        :param invoice: browse_record object of invoice
        :param invoices_group:
        :return: return dict of group invoice vals'''
        group_by_picking = context.get('group_by_picking')
        group_by_supplier = context.get('group_by_supplier')
        picking = lc.picking_info_id
        purchase = lc.purchase_order_info_id
        # the format of origin: PO1:PO2/Pick1:Pick2
        invoice_origin = invoice.origin
        if invoice_origin:
            invoice_origin = (purchase and purchase.name or '') + '|' + picking.name
        else:
            purchase_origin, picking_origin = invoice_origin.split('|')
            if purchase and purchase.name not in purchase_origin:
                purchase_origin += (':' + purchase.name)
            if picking.name not in picking_origin:
                picking_origin += (':' + picking.name)
            invoice_origin = '|'.join((purchase_origin, picking_origin))
        return {
            'name': invoice_origin,
            'origin': invoice_origin,
            'date_invoice': context.get('invoice_date', time.strftime('%Y-%m-%d')),
            'user_id': uid,
        }

    def _check_if_multi_currency(self, cr, uid, landed_cost_ids, default_currency_id, context=None):
        '''check all the landed costs if there is different currency inside.
        param default_currency_id: current user's company's deafult currency id.
        param landed_cost_ids: the ids of landed costs to be invoiced'''
        if not landed_cost_ids:
            return False
        else:
            res = {}
            lc_obj = self.pool.get('landed.cost.position')
            for lc in lc_obj.browse(cr, uid, landed_cost_ids, context=context):
                if lc.currency_id:
                    res[lc.currency_id.id] = True
                else:
                    res[default_currency_id] = True
            if len(res.keys()) > 1:
                return True
            return False

    def _generate_invoice_from_landed_cost(self, cr, uid, ids,
                                           context=None):
        """ Generate an invoice from order landed costs (means generic
        costs to a whole Incoming shipment) or from a line landed costs.
        
        :param ids: list of ids of landed costs
        :return: list of ids of invoices

        """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        invoice_ids = []
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        prod_obj = self.pool.get('product.product')
        lc_obj = self.pool.get('landed.cost.position')
        user_obj = self.pool.get('res.users')
        # invoices_group: {invoice_id: (partner_id, picking_id)}
        invoices_group = {}
        # products_group : {product_id: invoice_line_id}
        products_group = {}
        group_by_supplier = context.get('group_by_supplier', False)
        group_by_picking = context.get('group_by_picking', False)

        #get default currency id
        default_currency_id = user_obj.browse(cr, uid, uid, context=context).company_id.currency_id.id
        assert default_currency_id
        # check if there more than one currency in the list of landed costs.
        if self._check_if_multi_currency(cr, uid, ids, default_currency_id, context=context):
            raise orm.except_orm(
                ("Warning"),
                ("Please make sure there only one currency in the list of landed costs."))

        for landed_cost in lc_obj.browse(cr, uid, ids, context=context):
            # all landed costs should link to a stock picking and should have a supplier.
            if not landed_cost.partner_id or not landed_cost.picking_info_id:
                raise orm.except_orm(
                    _('Warning'),
                    _('You cannot create an invoice for'
                        ' the one without supplier or picking related!'))
            # invoices_group: {invoice_id: (partner_id, picking_id)}
            if group_by_supplier and not group_by_picking and \
                    (landed_cost.partner_id.id, False) in invoices_group.values():
                invoice_id = invoices_group.keys()[invoices_group.values().index((landed_cost.partner_id.id, False))]
                invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
                invoice_vals_group = self._prepare_group_invoice(
                    cr, uid, landed_cost, invoice, invoices_group, context=context)
                invoice.write(invoice_vals_group, context=context)

            elif group_by_supplier and group_by_picking and \
                    (landed_cost.partner_id.id, landed_cost.picking_info_id.id) in \
                    invoices_group.values():
                invoice_id = invoices_group.keys()[invoices_group.values().index(
                    (landed_cost.partner_id.id, landed_cost.picking_info_id.id))]
                invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
                invoice_vals_group = self._prepare_group_invoice(
                    cr, uid, landed_cost, invoice, invoices_group, context=context)
                invoice.write(invoice_vals_group, context=context)

            elif group_by_supplier and group_by_picking:
                invoice_vals = self._prepare_landed_cost_inv(
                    cr, uid, landed_cost, context=context)
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                invoices_group[invoice_id] = (landed_cost.partner_id.id, landed_cost.picking_info_id.id)

            else:
                invoice_vals = self._prepare_landed_cost_inv(
                    cr, uid, landed_cost, context=context)
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                invoices_group[invoice_id] = (landed_cost.partner_id.id, False)

            # get the fiscal position from supplier.
            fiscal_position = landed_cost.partner_id.property_account_position or False
            exp_account_id = prod_obj._choose_exp_account_from(
                cr, uid,
                landed_cost.product_id,
                fiscal_position=fiscal_position,
                context=context
            )
            # the merge of invoice line should be in the righ invoice.
            # products_group : {product_id: invoice_line_id}
            vals_line = self._prepare_landed_cost_inv_line(
                cr, uid, exp_account_id, invoice_id,
                landed_cost, context=context)
            if landed_cost.invoice_total_per_product and landed_cost.product_id.id not in products_group:
                invoice_line_id = invoice_line_obj.create(
                    cr, uid, vals_line,
                    context=context)
                products_group[landed_cost.product_id.id] = (invoice_id, invoice_line_id)
            # do the merge when in the same invoice and total_per_product..
            # should be in the same invoice.
            elif landed_cost.invoice_total_per_product and \
                    invoice_id == products_group[landed_cost.product_id.id][0]:

                invoice_line_id = products_group[landed_cost.product_id.id][1]
                invoice_line = invoice_line_obj.browse(cr, uid, invoice_line_id, context=context)
                qty_inv_line, price_unit_inv_line = invoice_line.quantity, invoice_line.price_unit
                tot_quantity = invoice_line.quantity + vals_line.get('quantity', 0)
                new_price_unit = (price_unit_inv_line * qty_inv_line + vals_line.get('price_unit', 0) * vals_line.get('quantity', 0)) / tot_quantity
                invoice_line_obj.write(
                    cr, uid, [invoice_line_id],
                    {
                        'price_unit': new_price_unit,
                        'quantity': qty_inv_line + vals_line.get('quantity', 0),
                    }, context=context)
            else:
                invoice_line_id = invoice_line_obj.create(
                    cr, uid, vals_line,
                    context=context)

            # hook write back the invoice_id
            landed_cost.write({'invoice_id': invoice_id}, context=context)
            invoice_ids.append(invoice_id)
        return list(set(invoice_ids))

    def _get_landed_inv_line_amount(self, landed_cost, inv, context=None):
        '''get the right amount '''
        pass

    def _prepare_landed_cost_inv_line(self, cr, uid, account_id, inv_id,
                                      landed_cost, context=None):
        """ Collects require data from landed cost position that is used to
        create invoice line for that particular position.

        If it comes from a stock move and Distribution type is per unit
        the quantity of the invoice is the stock move quantity

        :param account_id: Expense account.
        :param inv_id: Related invoice.
        :param browse_record landed_cost: Landed cost position browse record
        :return: Value for fields of invoice lines.
        :rtype: dict

        """
        cur_obj = self.pool.get('res.currency')
        # TODO unit test for this.
        inv = self.pool.get('account.invoice').browse(
            cr, uid, inv_id, context)
        assert inv
        qty = 1.0
        if landed_cost.move_id or landed_cost.purchase_order_line_id:
            line = landed_cost.move_id or landed_cost.purchase_order_line_id
            cost_type = landed_cost.distribution_type_id.landed_cost_type
            if cost_type == 'per_unit':
                qty = line.product_qty
            elif cost_type == 'volume':
                qty = line.line_volume
        line_tax_ids = [x.id for x in landed_cost.product_id.supplier_taxes_id]
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id
        default_currency_id = company_id.currency_id.id

        # amount on landed costs is in company's currency
        if default_currency_id == inv.currency_id.id:
            amount = landed_cost.amount

        # we don't convert for the rounding issue.
        elif landed_cost.currency_id and landed_cost.currency_id == inv.currency_id:
            amount = landed_cost.amount_currency
        elif landed_cost.currency_id and landed_cost.currency_id != inv.currency_id:
            # FIX NOTE which amount should be used to do the convert
            amount = cur_obj.compute(
                cr, uid, landed_cost.currency_id.id, inv.currency_id.id,
                landed_cost.amount_currency, context=context)
        else:
            amount = cur_obj.compute(
                cr, uid, default_currency_id, inv.currency_id.id,
                landed_cost.amount, context=context)
        return {
            'name': landed_cost.product_id.name,
            'account_id': account_id,
            'invoice_id': inv_id,
            'price_unit': amount or 0.0,
            'quantity': qty,
            'product_id': landed_cost.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, line_tax_ids)],
        }

    def _prepare_landed_cost_inv(self, cr, uid, landed_cost, context=None):
        """ Collects require data from landed cost position that is used to
        create invoice for that particular position.

        Note that _landed can come from a line or at whole PO level.

        :param browse_record landed_cost: Landed cost position browse record
        :return: Value for fields of invoice.
        :rtype: dict

        """
        order = landed_cost.picking_id or \
            landed_cost.move_id.picking_id
        if not order:
            order = (landed_cost.purchase_order_id or
                     landed_cost.purchase_order_line_id.order_id)
            raise orm.except_orm(
                ('Warning'),
                ('You cannot create invoice from here, please create invoices for the'
                    'landed costs from the stock picking.'))
        if not order:
            raise orm.except_orm(
                ('Warning'),
                ('Please link this '
                    'landed cost: %s to a stock picking or stock move.' % (landed_cost.product_id.name)))
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        company_id = order and order.company_id or user.company_id
        inv_name = order and order.name or 'Landed costs'
        fiscal_position_id = landed_cost.partner_id.property_account_position and \
            landed_cost.partner_id.property_account_position.id or False
        journal_obj = self.pool.get('account.journal')
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        default_currency_id = company_id.currency_id.id
        # First get the journal from wizard how to assign the journal
        journal_id = context.get('journal_id')
        if not journal_id:
            journal_ids = journal_obj.search(
                cr, uid,
                [('type', '=', 'purchase'),
                 ('company_id', '=', company_id.id)],
                limit=1)
            if not journal_ids:
                raise orm.except_orm(
                    _('Error!'),
                    _('Define purchase journal for this company: "%s" (id: %d).')
                    % (company_id.name, company_id.id))
            journal_id = journal_ids and journal_ids[0]
        return {
            # get the currency from landed cost first.
            'currency_id': landed_cost.currency_id.id or default_currency_id,
            'partner_id': landed_cost.partner_id.id,
            'account_id': landed_cost.partner_id.property_account_payable.id,
            'type': 'in_invoice',
            'origin': inv_name,
            'fiscal_position': fiscal_position_id,
            'company_id': company_id.id,
            'journal_id': journal_id,
            'date_invoice': context.get('invoice_date')
        }
