# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from tools.translate import _
import openerp.addons.decimal_precision as dp

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    _columns = {
        'po_price_modification_limit':fields.boolean("No control on PO price", help="""If checked, allows you to change the price in PO (only when either the Supplier or Product allow it)"""),
    }

    _defaults = {
        'po_price_modification_limit': True,
    }
res_partner()

class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"

    _columns = {
        'po_price_modification_limit':fields.boolean("No control on PO price", help="""If checked, allows you to change the price in PO (only when either the Supplier or Product allow it)."""),
    }

    _defaults = {
        'po_price_modification_limit': True
    }

product_product()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    _order = 'order_id desc, sequence'

    def _price_unit_line_without_tax(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj._unit_compute(cr, uid, line.taxes_id, line.price_unit, product=None, partner=None, quantity=0)
            cur = line.order_id.pricelist_id.currency_id
            print taxes and taxes[0] and taxes[0]['amount'] or 0
            pu_wt = line.price_unit - (taxes and taxes[0] and taxes[0]['amount'] or 0)
            res[line.id] = cur_obj.round(cr, uid, cur, pu_wt)
        return res

    def _amount_line_with_tax(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, line.order_id.partner_id, force_excluded=True)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    def _qty_received(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            qty = 0.0
            for move in line.move_ids:
                if move.state == 'done':
                    qty += move.product_qty
            res[line.id] = qty
        return res
    
    def _qty_unreceived(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            qty = 0.0
            for move in line.move_ids:
                if move.state not in ('done', 'cancel'):
                    qty += move.product_qty
            res[line.id] = qty
        return res

    _columns = {
        'modify_price': fields.boolean('Modify Price'),
        'sequence': fields.integer('Sequence', help="Sequence for order in view and print report"),
        'amount_subtotal': fields.function(_amount_line_with_tax, string='Subtotal(Inc. Tax)', type='float', digits_compute=dp.get_precision('Account')),
        'qty_received': fields.function(_qty_received, string='Reception Qty', type='float', digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_unreceived': fields.function(_qty_unreceived, string='Waiting Qty', type='float', digits_compute=dp.get_precision('Product Unit of Measure')),
        'price_unit_original': fields.float('Original Unit Price', digits_compute=dp.get_precision('Product Price')),
        'price_unit_exclude_tax': fields.function(_price_unit_line_without_tax, string='Unit Price(Exc. Tax)', type='float', digits_compute=dp.get_precision('Product Price')),
    }
    _defaults = {
        'sequence': 1,
        'modify_price': False,
    }    

    
    def onchange_price_unit(self, cr, uid, ids, partner_id, product_id, price_unit_original, price_unit, context=None):
        #Not use at the moment! add a readonly attribute in view definition!
        context = context or {}
        res = {}
        
        if not partner_id and not product_id:
            return res
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        
        if not product.po_price_modification_limit and not partner.po_price_modification_limit and price_unit_original != price_unit:
            res['value'] = {'price_unit': price_unit_original}
            res['warning'] = {'title' : _('PO Price'), 'message' : _('You can not modify the price of this product sold by this supplier !')}
            #raise osv.except_osv(_('Error!'), _('You can not modify the price of this product sold by this supplier !'))
        else:
            res['value'] = {'price_unit_original':price_unit}

        return res

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)

        if not product_id or not partner_id:
            return res

        res_partner = self.pool.get('res.partner')
        partner = res_partner.browse(cr, uid, partner_id)
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id, context=context)

        modify_price = not product.po_price_modification_limit and not partner.po_price_modification_limit
        res['value'].update({'modify_price': modify_price})

        if res and 'value' in res and 'price_unit' in res['value']:
            print "AAAAAAAAAAAA"
            res['value'].update({'price_unit_original': res['value']['price_unit']})
        print "BBBBBBBBBBBBBB%s"%res

        return res


purchase_order_line()
