# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


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
        
        'supply_method': fields.selection([('produce','Produce'),('buy','Buy')], 'Supply method', states={'draft':[('readonly',False)], 'confirmed':[('readonly',False)], 'exception':[('readonly',False)]},
            readonly=True,),
        'procure_method': fields.selection([('make_to_stock','Make to Stock'),('make_to_order','Make to Order')], 'Procurement Method', states={'draft':[('readonly',False)], 'confirmed':[('readonly',False)], 'exception':[('readonly',False)]},
            readonly=True, required=True, help="If you encode manually a Procurement, you probably want to use" \
            " a make to order method."),

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

    def button_done(self, cr, uid, ids, context=None):
        """ Changes procurement state to Done and writes Closed date.
            Solve the service bug !
        @return: True
        """
        if not self.check_move_done(cr, uid, ids, context):
            return False
        move_obj = self.pool.get('stock.move')
        for procurement in self.browse(cr, uid, ids):
            if procurement.move_id:
                if procurement.close_move and (procurement.move_id.state <> 'done'):
                    move_obj.action_done(cr, uid, [procurement.move_id.id])
        res = self.write(cr, uid, ids, {'state': 'done', 'date_close': time.strftime('%Y-%m-%d')})
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_trigger(uid, 'procurement.order', id, cr)
        return res


    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            newdate = datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.product_id.produce_delay or 0.0)
            newdate = newdate - relativedelta(days=company.manufacturing_lead)
            produce_id = production_obj.create(cr, uid, {
                'origin': procurement.origin,
                'product_id': procurement.product_id.id,
                'product_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                'location_src_id': procurement.location_id.id,
                'location_dest_id': procurement.location_id.id,
                'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                'move_prod_id': res_id,
                'company_id': procurement.company_id.id,
            })
            
            res[procurement.id] = produce_id
            self.write(cr, uid, [procurement.id], {'state': 'running', 'production_id': produce_id})   
        self.production_order_create_note(cr, uid, ids, context=context)
        return res


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


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _hook_create_post_procurement(
            self, cr, uid, production, procurement_id, context=None):
        '''inherit this api, write back the supply_method to the procurement order'''
        if procurement_id:
            procurement_obj = self.pool.get('procurement.order')
            procurement_order = procurement_obj.browse(
                cr, uid, procurement_id, context=context)
            product_id = procurement_order.product_id
            supply_method = product_id.supply_method
            procurement_order.write({'supply_method': supply_method}, context=context)
        return super(mrp_production, self)._hook_create_post_procurement(
            cr, uid, production, procurement_id, context=context)


