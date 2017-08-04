# -*- coding: utf-8 -*-
# © 2014 Elico Corp(https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
import time


class StockMove(osv.osv):
    _inherit = 'stock.move'

    def product_id_change(self, cr, uid, ids, product, location_id,
                          location_dest_id, date_expected, context=None):
        context = context or {}
        result = {}

        product_obj = self.pool.get('product.product').browse(
            cr, uid, product, context=context)
        if product_obj and product_obj.uom_id:
            result['product_uom'] = product_obj.uom_id.id
        result['name'] = product_obj.name
        result['location_id'] = location_id
        result['location_dest_id'] = location_dest_id
        result['date_expected'] = date_expected
        return {'value': result}

StockMove()



