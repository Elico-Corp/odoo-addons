# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Chen Rong <chen.rong@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
from datetime import datetime, timedelta
import time
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID

class product_template(osv.Model):

    _inherit = 'product.template'

    def _user_product_price(self, cr, uid, ids, name, arg, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        product = self.browse(cr, uid, ids, context=context)
        price = ''
        res= {}
        for p in product:
            product = p.product_variant_ids[0]
            if user.property_product_pricelist:
                price = self.pool.get('product.pricelist').price_get(cr, SUPERUSER_ID, [user.property_product_pricelist.id],
                        product.id, 1.0, user.partner_id.id, {
                            'uom': product.uom_id.id,
                            'date': fields.datetime.now,
                            })[user.property_product_pricelist.id]
                if price is False:
                    price = product.price
            res[p.id] = price
        return res
    _columns = {'user_price': fields.function(_user_product_price, type='float', string='Price', digits_compute=dp.get_precision('Product Price'))}
