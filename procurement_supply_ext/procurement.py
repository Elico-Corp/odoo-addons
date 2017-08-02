# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-Today Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
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

from osv import osv, fields
import time
import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta

from tools.translate import _

class procurement_order(osv.osv):
    """
    Procurement Orders
    """
    _inherit = "procurement.order"
    _columns = {
        
        'supply_method': fields.selection([('produce','Produce'),('buy','Buy')], 'Supply method', required=True, states={'draft':[('readonly',False)], 'confirmed':[('readonly',False)]},
            readonly=True,),
    }
    
    def init(self, cr):
        cr.execute('''update procurement_order set supply_method = pt.supply_method from product_product pp, product_template pt
                        where procurement_order.supply_method is null and procurement_order.product_id = pp.id and pp.product_tmpl_id = pt.id''')

    def check_produce(self, cr, uid, ids, context=None):
        """ Checks product type.
        @return: True or Product Id.
        """
        res = True
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for procurement in self.browse(cr, uid, ids, context=context):
            supply_method = procurement.supply_method or procurement.product_id.product_tmpl_id.supply_method or False
            if supply_method <> 'produce':
                partner_list = sorted([(partner_id.sequence, partner_id) for partner_id in  procurement.product_id.seller_ids if partner_id])
                if partner_list:
                    partner = partner_list and partner_list[0] and partner_list[0][1] and partner_list[0][1].name or False
                    if user.company_id and user.company_id.partner_id:
                        if partner.id == user.company_id.partner_id.id:
                            return True
                return False
            if procurement.product_id.product_tmpl_id.type=='service':
                res = res and self.check_produce_service(cr, uid, procurement, context)
            else:
                res = res and self.check_produce_product(cr, uid, procurement, context)
            if not res:
                return False
        return res

    def check_buy(self, cr, uid, ids):
        """ Checks product type.
        @return: True or Product Id.
        """
        user = self.pool.get('res.users').browse(cr, uid, uid)
        partner_obj = self.pool.get('res.partner')
        for procurement in self.browse(cr, uid, ids):
            supply_method = procurement.supply_method or procurement.product_id.product_tmpl_id.supply_method or False
            if supply_method  <> 'buy':
                return False
            if not procurement.product_id.seller_ids:
                cr.execute('update procurement_order set message=%s where id=%s',
                        (_('No supplier defined for this product !'), procurement.id))
                return False
            partner = procurement.product_id.seller_id #Taken Main Supplier of Product of Procurement.

            if not partner:
                cr.execute('update procurement_order set message=%s where id=%s',
                           (_('No default supplier defined for this product'), procurement.id))
                return False

            if user.company_id and user.company_id.partner_id:
                if partner.id == user.company_id.partner_id.id:
                    return False

            address_id = partner_obj.address_get(cr, uid, [partner.id], ['delivery'])['delivery']
            if not address_id:
                cr.execute('update procurement_order set message=%s where id=%s',
                        (_('No address defined for the supplier'), procurement.id))
                return False
        return True
    
procurement_order()

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def action_ship_create(self, cr, uid, ids, *args):
        if super(sale_order, self).action_ship_create(cr, uid, ids, *args):
            proc_obj = self.pool.get('procurement.order')
            for order in self.browse(cr, uid, ids, context={}):
                for line in order.order_line:
                    if line.procurement_id and line.product_id:
                        proc_obj.write(cr, uid, [line.procurement_id.id], {'supply_method': line.product_id.supply_method})
        return True
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
