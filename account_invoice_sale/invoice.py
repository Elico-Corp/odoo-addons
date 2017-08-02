# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author:            Andy Lu <andy.lu@elico-corp.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, osv
import netsvc

class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'

    def _get_sale_id(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if not ids:
            return res

        for id in ids:
            res[id] = False
        cr.execute('''SELECT r.invoice_id as line_id,d.order_id as sale_id
                FROM sale_order_line_invoice_rel r
                inner join sale_order_line d on r.order_line_id = d.id
                WHERE r.invoice_id IN %s ''', (tuple(ids),))

        for item in cr.fetchall():
            res[item[0]] = item[1]
        return res

#    def _get_purchase_id(self, cr, uid, ids, name, arg, context=None):
#    logger = netsvc.Logger()
#    def _get_sale_id(self, cr, uid, ids, name, arg, context=None):
#        res = {}
#        if not ids:
#            return res
#        self.logger.notifyChannel('IDS 4 ' + self._name, netsvc.LOG_INFO, str(ids))
#        for id in ids:
#            res[id] = False
#        cr.execute('''SELECT r.invoice_id as line_id,d.order_id as sale_id
#                FROM sale_order_line_invoice_rel r
#                inner join sale_order_line d on r.order_line_id = d.id
#                WHERE r.invoice_id IN %s ''', (tuple(ids),))
#        sale_obj = self.pool.get('sale.order')
#        sale_name = {}
#        for item in cr.fetchall():
#            self.logger.notifyChannel('Sale 4 ' + self._name, netsvc.LOG_INFO, str(item))
#            res[item[0]] = item[1]
#        return res

    _columns = {
        'sale_id': fields.function(_get_sale_id, method=True, string='Sale Order',
            type='many2one', relation='sale.order'),
#        'purchase_id': fields.function(_get_purchase_id, method=True, string='Purchase Order',
#            type='many2one', relation='purchase.order'),
    }

account_invoice_line()
