# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields


class landed_costs_reporting(orm.Model):
    _name = 'landed.costs.reporting'
    _inherit = 'landed.cost.position'

    def _get_purchase_price_in_reporting_currency(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        if not ids:
            return res
        currency_obj = self.pool.get('res.currency')
        for lc_reporting in self.browse(cr, uid, ids, context=context):
            from_currency = lc_reporting.purchase_price_currency
            from_currency_id = from_currency and from_currency.id or False
            to_currency = lc_reporting.default_currency_id
            to_currency_id = to_currency and to_currency.id or False
            from_amount = lc_reporting.purchase_price
            to_amount = currency_obj.compute(
                cr, uid, from_currency_id, to_currency_id,
                from_amount, round=True, context=context)
            res[lc_reporting.id] = to_amount
        return res

    _columns = {
        'date': fields.related(
            'move_id', 'date', type="datetime",
            relation='stock.move', string='Date',
            store={
                'landed.costs.reporting': (lambda self, cr, uid, ids, c={}: ids, ['move_id'], 20),
            }),
        'duty_zone_id': fields.related(
            'move_id', 'location_dest_id', 'duty_zone_id', type="many2one",
            relation='stock.duty.zone',
            string="Duty Zone",
            store={
                'landed.costs.reporting': (lambda self, cr, uid, ids, c={}: ids, ['move_id'], 20),
            }),
        'main_product_id': fields.related(
            'move_id', 'product_id', string="Product", type="many2one",
            relation='product.product',
            store={
                'landed.costs.reporting': (lambda self, cr, uid, ids, c={}: ids, ['move_id'], 20),
            }),
        'line_volume': fields.related(
            'move_id', 'line_volume', type="float", string="Total Volume",
            relation='stock.move',
            store={
                'landed.costs.reporting': (lambda self, cr, uid, ids, c={}: ids, ['move_id'], 20),
            }),
        'period_id': fields.many2one(
            'account.period', 'Period'),
        # type from function to normal float fields
        'amount_company_currency': fields.float('Amount Company Currency'),
        'amount_total': fields.float('Amount Total (Reporting Currency)'),
        'amount_total_comp_currency': fields.float(
            'Amount Total Company Currency'),
        'picking_info_id': fields.many2one('stock.picking', 'Picking'),
        'purchase_order_info_id': fields.many2one('purchase.order', 'Purchase'),
        'total_value': fields.float('Total Value (Reporting Currency)'),
        'total_quantity': fields.float('Total quantity'),
        # todo add the total value.
        'purchase_price': fields.related(
            'move_id',
            'purchase_line_id', 'price_unit', type="float",
            string="Purchase Price", relation="purchase.order.line",
            store=True),
        'purchase_price_currency': fields.related(
            'purchase_order_info_id', 'currency_id', type="many2one",
            string="Purchase Currency", relation='res.currency', store=True),
        'purchase_price_in_reporting_currency': fields.function(
            _get_purchase_price_in_reporting_currency, type='float',
            string='Purchase Price (Reporting currency)'),
    }
