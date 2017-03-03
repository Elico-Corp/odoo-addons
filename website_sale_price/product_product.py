# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields


class ProductTemplate(osv.Model):
    _inherit = 'product.template'

    def _user_product_price(self, cr, uid, ids, name, arg, context=None):
        user = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        product = self.browse(cr, uid, ids, context=context)
        price = ''
        res = {}
        for p in product:
            product = p.product_variant_ids[0]
            if user.property_product_pricelist:
                price = \
                    self.pool.get('product.pricelist').price_get(
                        cr, SUPERUSER_ID,
                        [user.property_product_pricelist.id],
                        product.id, 1.0, user.partner_id.id, {
                            'uom': product.uom_id.id,
                            'date': fields.datetime.now,
                        })[user.property_product_pricelist.id]
                if price is False:
                    price = product.price
            res[p.id] = price
        return res

    _columns = {'user_price': fields.function(
        _user_product_price,
        type='float',
        string='Price',
        digits_compute=dp.get_precision('Product Price'))
    }
