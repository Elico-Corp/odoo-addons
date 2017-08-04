# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import fields, orm, osv
from tools.translate import _
import decimal_precision as dp


class product_search(orm.Model):
    _name = "product.search"
    _description = "Product Price Search"

    def action_button_search(self, cr, uid, ids, context=None):
        context = context or {}
        if not isinstance(ids, list):
            ids = [ids]

        psl_pool = self.pool.get('product.search.line')
        for id in ids:
            search = self.browse(cr, 1, id)
            pricelist_id = search.pricelist_id.id
            product_id = search.product_id.id
            qty = search.qty
            search = search.id
        remove_ids = self.search(cr, uid, [('id', '!=', search)],
                                 context=context)
        self.unlink(cr, uid, remove_ids, context=context)
        remove_ids = psl_pool.search(cr, uid, [('search_id', '=', search)],
                                     context=context)
        psl_pool.unlink(cr, uid, remove_ids, context=context)

        strlist = qty.replace(' ', '')
        strlist = strlist.replace(',,', ',0,')
        strlist = strlist.replace(',,', ',0,')
        if strlist[-1] == ',':
            strlist += '0'
        if strlist[0] == ',':
            str2 = '0'
            str2 += strlist
            strlist = str2
        strlist = strlist.split(',')

        for qty in strlist:
            if qty.isdigit():
                price = self.pool.get(
                    'product.pricelist').price_get(
                    cr, uid, [pricelist_id], product_id, qty)[pricelist_id]

                self.pool.get('product.search.line').create(cr, uid, {
                    'product_id': product_id,
                    'pricelist_id': pricelist_id,
                    'qty': qty,
                    'price_unit': price,
                    'search_id': search
                })
            else:
                raise osv.except_osv(
                    _('Error Input'),
                    _('Please check your product qty input is correct'))
        return True

    _columns = {
        'name': fields.char('Order Reference', size=64),
        'product_id': fields.many2one(
            'product.product', 'Product',
            domain=[('sale_ok', '=', True)], change_default=True),
        'pricelist_id': fields.many2one(
            'product.pricelist', 'Pricelist',
            domain=[('visible', '=', True)],
            required=True, help="Pricelist for current sales order."),
        'search_line': fields.one2many(
            'product.search.line', 'search_id',
            'Search Lines', readonly=True),
        'price_unit': fields.float(
            'Price Unit', required=True,
            digits_compute=dp.get_precision('Sale Price')
        ),
        'qty': fields.char(
            'Product Qty',
            help="Comma separated values of quantity. eg:100,1000,5000,10000",
            size=128, required=True,),
    }

    _defaults = {
        'qty': '0'
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Order Reference must be unique !'),
    ]
    _order = 'name desc'


class product_search_line(orm.Model):
    _name = 'product.search.line'
    _description = 'Product Search Line'

    _columns = {
        'search_id': fields.many2one(
            'product.search', 'Search Reference', required=True,
            ondelete='cascade', select=True, readonly=True
        ),
        'product_id': fields.many2one(
            'product.product', 'Product', domain=[('sale_ok', '=', True)],
            change_default=True),
        'pricelist_id': fields.many2one(
            'product.pricelist', 'Pricelist', required=True,
            help="Pricelist for current sales order."),
        'qty': fields.float(
            'Product Qty', required=True,
            digits_compute=dp.get_precision('Sale Price'),),
        'price_unit': fields.float(
            'Price Unit', required=True,
            digits_compute=dp.get_precision('Sale Price'),),
    }


class product_pricelist(orm.Model):
    _name = "product.pricelist"
    _description = "Pricelist"
    _inherit = "product.pricelist"

    _columns = {
        "visible": fields.boolean("Visible in Pricelist inquiry form"),
    }
