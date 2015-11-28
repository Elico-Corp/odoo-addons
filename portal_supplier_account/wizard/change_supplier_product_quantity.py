# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Qing Wang <qing.wang@elico-corp.com>
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
import openerp.addons.decimal_precision as dp


class change_supplier_product_quantity(osv.osv_memory):
    _name = "supplier.change.product.qty"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'new_quantity': fields.float(
            'New Quantity on Hand',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True,
            help='This quantity is expressed in the Default Unit of Measure of\
             the product.'),
    }

    _defaults = {
        'new_quantity': 1,
        'product_id': lambda self, cr, uid, ctx: ctx and ctx.get('active_id', False) or False
    }

    def change_product_qty(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.pool.get('product.product').write(
                cr, uid, [context.get('active_id')],
                {'supplier_stock_count': obj.new_quantity})

