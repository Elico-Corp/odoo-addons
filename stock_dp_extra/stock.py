# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import decimal_precision as dp
from osv import fields, orm


class stock_move(orm.Model):
    _inherit = "stock.move"
    _name = "stock.move"

    _columns = {
        'price_unit': fields.float(
            'Unit Price',
            digits_compute=dp.get_precision('Stock Move'),
            help="Technical field used to record the product cost set by the\
                  user during a picking confirmation (when average price \
                  costing method is used)")
    }

    def _get_reference_accounting_values_for_valuation(self, cr, uid, move,
                                                       context=None):
        """
        Return the reference amount and reference currency representing the
        inventory valuation for this move.
        These reference values should possibly be converted before being posted
        in Journals to adapt to the primary
        and secondary currencies of the relevant accounts.
        """
        product_uom_obj = self.pool.get('product.uom')

        # by default the reference currency is that of the move's company
        reference_currency_id = move.company_id.currency_id.id

        default_uom = move.product_id.uom_id.id
        qty = product_uom_obj._compute_qty(
            cr, uid, move.product_uom.id, move.product_qty, default_uom)

        # if product is set to average price and a specific value was entered
        # in the picking wizard,
        # we use it
        if move.product_id.cost_method == 'average' and move.price_unit:
            reference_amount = qty * move.price_unit
            reference_currency_id = move.price_currency_id.id\
                or reference_currency_id

        # Otherwise we default to the company's valuation price type
        # considering that the values of the
        # valuation field are expressed in the default currency of the move's
        # company.
        else:
            if context is None:
                context = {}
            amount_unit = move.product_id.price_get(
                'standard_price', context=context)[move.product_id.id]
            reference_amount = amount_unit * qty

        return reference_amount, reference_currency_id


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        res = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
        if picking.sale_id:
            if picking.sale_id.user_id:
                res['user_id'] = picking.sale_id.user_id.id
            if picking.sale_id.section_id:
                res['section_id'] = picking.sale_id.section_id.id
        return res
