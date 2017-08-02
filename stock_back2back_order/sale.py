# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"
    _name = "sale.order"
    
    def _picked_rate(self, cr, uid, ids, name, arg, context=None):
        if not ids:
            return {}
        res = {}
        for id in ids:
            res[id] = [0.0, 0.0]
        cr.execute('''SELECT
                p.sale_id, sum(m.product_qty), m.state as mp_state
            FROM
                stock_move m
            LEFT JOIN
                stock_picking p on (p.id=m.picking_id)
            WHERE
                p.type = 'out' and p.sale_id IN %s GROUP BY m.state, p.sale_id''', (tuple(ids),)) # Only count out progress. Ian@Elico
        for oid, nbr, mp_state in cr.fetchall():
            if mp_state == 'cancel':
                continue
            if mp_state == 'done':
                res[oid][0] += nbr or 0.0
                res[oid][1] += nbr or 0.0
            else:
                res[oid][1] += nbr or 0.0
        for r in res:
            if not res[r][1]:
                res[r] = 0.0
            else:
                res[r] = 100.0 * res[r][0] / res[r][1]
        for order in self.browse(cr, uid, ids, context=context):
            if order.shipped:
                res[order.id] = 100.0
        return res

    # Apparently if I don't put the column definition here, the function above will not work. Ian@Elico
    _columns = {
        'picked_rate': fields.function(_picked_rate, method=True, string='Picked', type='float'),
    }
    
sale_order()

