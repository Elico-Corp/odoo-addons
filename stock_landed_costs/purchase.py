# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _prepare_landed_costs(self, cr, uid, order, context=None):
        '''prepare the landed costs from the purchase order line to stock move
        prepare the landed costs from the purchase order to incoming shipment
        :param order: this can be object purchase order or purchase order line.'''

        assert hasattr(order, 'landed_cost_line_ids'), 'Model must have field landed_cost_line_ids!'
        res = []

        def get_id(obj):
            return obj and obj.id or False

        def get_purchase_id(landed_cost):
            if landed_cost.purchase_order_id:
                return get_id(landed_cost.purchase_order_id)

            elif landed_cost.purchase_order_line_id:
                purchase = landed_cost.purchase_order_line_id.order_id
                return purchase and purchase.id
            else:
                return False

        # convert the amount to company's default currency
        for landed_cost in order.landed_cost_line_ids:
            lc_value = {
                'account_id': get_id(landed_cost.account_id),
                'active': landed_cost.active,
                'amount': landed_cost.amount_company_currency,
                'amount_company_currency': landed_cost.amount_company_currency,
                'amount_currency': landed_cost.amount_currency,
                'amount_total': landed_cost.amount_total,
                'amount_total_comp_currency': landed_cost.amount_total_comp_currency,
                'company_id': get_id(landed_cost.company_id),
                'currency_id': get_id(landed_cost.currency_id),
                'date_po': landed_cost.date_po,
                'distribution_type_id': get_id(landed_cost.distribution_type_id),
                'generate_invoice': landed_cost.generate_invoice,
                'invoice_id': False,
                'move_id': get_id(landed_cost.move_id),
                'partner_id': get_id(landed_cost.partner_id),
                'picking_id': get_id(landed_cost.picking_id),
                'po_currency_id': get_id(landed_cost.po_currency_id),
                'po_pricelist_id': get_id(landed_cost.po_pricelist_id),
                'product_id': get_id(landed_cost.product_id),
                'purchase_order_info_id': get_purchase_id(landed_cost),
                'purchase_order_line_id': False,
                'shipment_id': get_id(landed_cost.shipment_id),
                'template_id': get_id(landed_cost.template_id),
                'invoice_total_per_product': landed_cost.invoice_total_per_product
            }
            res.append((0, 0, lc_value))
        # if the amount_currency is the same as company's default currency, we don't do the calculation.
        return res

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        '''copy the landed costs on purchase order line to stock move'''
        res = super(purchase_order, self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, context=context)
        res['landed_cost_line_ids'] = self._prepare_landed_costs(
            cr, uid, order_line, context=context)
        # pass the purchase order's currency
        currency = order_line.order_id.currency_id
        res['price_currency_id'] = currency and currency.id or False
        res['purchase_amount_untaxed'] = order_line.order_id.amount_total
        res['purchase_line_subtotal'] = order_line.price_subtotal
        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        '''copy the landed costs on purchase order to stock picking'''
        res = super(purchase_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        res['landed_cost_line_ids'] = self._prepare_landed_costs(cr, uid, order, context=context)
        return res

    _columns = {
        'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'purchase_order_id',
            'Landed Costs',
            readonly=True,
            states={'draft': [('readonly', False)]},
            domain=[('purchase_order_line_id', '=', False)])
    }


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'purchase_order_line_id',
            'Landed Costs Positions',
            readonly=True,
            states={'draft': [('readonly', False)]}),
    }
