# -*- coding: utf-8 -*-
# © 2011 Cubic ERP - Teradata SAC(http://cubicerp.com)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from tools.translate import _
import time
from datetime import datetime
from datetime import timedelta

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    _columns = {
        'pts_id':   fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts')]),
        'dts_id':   fields.many2one('delivery.time', 'Delivery Time', select=True, domain=[('type', '=', 'dts')]),
    }
stock_move()


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _name = "stock.picking"
    
    def action_pop_order(self, cr, uid, ids, context=None):
        mo_ids = False
        context = context or {}
        
        id = ids or context.get('active_ids', False) or False
        if id:        
            for picking in self.browse(cr, uid, [id[0]], context=context):
                if picking.sale_id:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _("Related Sale Order"),
                        'view_mode': 'form,tree',
                        'view_id': False,
                        'view_type': 'form',
                        'res_model': 'sale.order',
                        'res_id': picking.sale_id.id,
                        'context': context
                    }
                elif picking.purchase_id:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _("Related Purchase Order"),
                        'view_mode': 'form,tree',
                        'view_id': False,
                        'view_type': 'form',
                        'res_model': 'purchase.order',
                        'res_id': picking.purchase_id.id,
                        'context': context
                    }            
        return {}
    
    def _get_route_line_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            sql_req = """SELECT c.id AS func_id
                        FROM delivery_route_line c
                        WHERE (c.picking_id = %d)""" % (i,)
            cr.execute(sql_req)
            sql_res = cr.dictfetchone()

            if sql_res:
                res[i] = sql_res['func_id']
            else:
                res[i] = False
        return res
        
    def _get_route_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            sql_req = """SELECT r.id AS func_id
                        FROM delivery_route_line c, delivery_route r
                        WHERE c.route_id = r.id and (c.picking_id = %d)""" % (i,)
            cr.execute(sql_req)
            sql_res = cr.dictfetchone()

            if sql_res:
                res[i] = sql_res['func_id']
            else:
                res[i] = False
        return res
                
    def _get_route_state(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            sql_req = """SELECT c.state AS func_id
                        FROM delivery_route_line c
                        WHERE (c.picking_id = %d)""" % (i,)
            cr.execute(sql_req)
            sql_res = cr.dictfetchone()

            if sql_res:
                res[i] = sql_res['func_id']
            else:
                res[i] = False
        return res
    
    
    def _get_is_collected(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for pick in self.browse(cr, uid, ids):
            result[pick.id] = pick.purchase_id and pick.purchase_id.is_collected or False
        return result
    
    def _pick_to_update_after_po_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('stock.picking').search(cr, uid, [('purchase_id', 'in', ids)]) or []
    
    _store_is_collected = {
        'stock.picking': (lambda self, cr, uid, ids, context: ids, ['purchase_id'], 10),
        'purchase.order': (_pick_to_update_after_po_change, ['is_collected'], 10),
    }
    
    _columns = {
        'delivery_date': fields.date('Delivery Date'),
        'pts_id': fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts')]),
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', help='Delivery time or turn to receive', domain=[('type', '=', 'dts')]),
        'route_line_id': fields.function(_get_route_line_id, type='many2one', obj='delivery.route.line', method=True, string='Delivery Route Line', readonly=True, store=False),
        'route_id': fields.function(_get_route_id, type='many2one', obj='delivery.route', method=True, string='Delivery Route', readonly=True, store=False),
        'route_state' : fields.function(_get_route_state, type="char", method=True, string="Route State", readonly=True, store=False),
        'delivered': fields.boolean('Is Delivered', select=True),
        'street': fields.related('partner_id', 'street', type='char', size=128, string='Street'),
        'delivered_cpt': fields.integer('Delivered x times'),
        'delivery_state': fields.selection([("not_planned", _("Not planned")), ("planned", _("Planned")), ("in_del", _("In delivery")), ("del_ok", _("Delivered")), ("del_ex", _("Exception")), ("del_rt", _("Returned")), ("del_rt_exp", _("No redelivery"))], 'Delivery State'),
        'carrier_id': fields.many2one('delivery.carrier', 'Carrier'),
        'is_collected': fields.function(_get_is_collected, type='boolean', multi=False, store=_store_is_collected, string='Is Collected'),
    }
    _defaults = {
        'delivered': False,
        'delivered_cpt': 0,
        'delivery_state': "not_planned",
    }

#    def write(self, cr, uid, ids, vals, context=None):
#        if 'delivered' in vals.keys():
#            for o in self.browse(cr, uid, ids, context=context):
#                if o.route_line_id:
#                    raise osv.except_osv(_('Invalid action !'), _('Cannot update a Picking(s) which are already delivery routed (%s) !'%o.route_id.name))
#        return  super(stock_picking, self).write(cr, uid, ids, vals, context=context)

    
    def unlink(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            if o.route_line_id:
                self.pool.get('delivery.route.line').unlink(cr, uid, [o.route_line_id.id], context=context)
        return super(stock_picking, self).unlink(cr, uid, ids, context=context)
    
    
    def search(self, cr, uid, args, offset=0, limit=None, order='name', context=None, count=False):
        context = context or {}
        new_args = []
        if 'update_pts' in context and len(args) > 1:
            for arg in args:
                if arg[0] != 'id':
                    new_args.append(arg)
        else:
            new_args = args
        return super(stock_picking, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
        
    
#    def _read_group_dts_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
#        context = context or {}
#        domain  = domain or []
#        delivery_ids  = []
#        delivery_ids2 = []
#        has_dts_set   = False
#        delivery_obj = self.pool.get('delivery.time')
#        if domain:
#            for arg in domain:
#                if arg[0] == 'dts_id.start_date':
#                    min_date = datetime.now().strftime('%Y-%m-%d') + ' 00:00:00'
#                    #max_date = datetime.now() + timedelta(days=1)
#                    max_date = datetime.now().strftime('%Y-%m-%d') + ' 23:59:59'        
#                    cr.execute("SELECT id FROM delivery_time WHERE type='dts' AND active=True AND start_date>='" + min_date + "' AND start_date<='" + max_date + "'")
#                    delivery_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
#                elif arg[0] == 'dts_id':
#                    has_dts_set = [(arg[0],arg[1],arg[2])]
#        fold = {}
#        
#        if has_dts_set:
#            delivery_ids2 = delivery_obj.search(cr, uid, has_dts_set)
#            if delivery_ids2:
#                for id in delivery_ids:
#                    if id not in delivery_ids2:
#                        fold[id] = True
#                delivery_ids.extend(delivery_ids2)
#        result = delivery_obj.name_get(cr, uid, delivery_ids, context=context)
#        return result, fold
#    
#    
#    _group_by_full = {
#        'dts_id': _read_group_dts_ids,
#    }
stock_picking()


class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _name = "stock.picking.out"

    _columns = {
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', help='Delivery time or turn to receive', domain=[('type', '=', 'dts')]),
        'pts_id':   fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts')]),
        'delivery_state': fields.selection([("not_planned", _("Not yet planned for delivery")), ("planned", _("Planned for delivery")), ("in_del", _("In delivery")), ("del_ok", _("Delivered")), ("del_ex", _("Delivered with exception")), ("del_rt", _("Delivered and returned")), ("del_rt_exp", _("Returned, no delivery"))], 'Delivery State'),
        'carrier_id': fields.many2one('delivery.carrier', 'Carrier'),
    }
    _defaults = {
        'delivery_state': "not_planned",
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order='name', context=None, count=False):
        context = context or {}
        new_args = []
        if 'update_pts' in context and len(args) > 1:
            for arg in args:
                if arg[0] != 'id':
                    new_args.append(arg)
        else:
            new_args = args
        return super(stock_picking_out, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
    
#    def _read_group_dts_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
#        context = context or {}
#        domain  = domain or []
#        delivery_ids  = []
#        delivery_ids2 = []
#        has_dts_set   = False
#        delivery_obj = self.pool.get('delivery.time')
#        if domain:
#            for arg in domain:
#                if arg[0] == 'dts_id.start_date':
#                    min_date = datetime.now().strftime('%Y-%m-%d') + ' 00:00:00'
#                    #max_date = datetime.now() + timedelta(days=1)
#                    max_date = datetime.now().strftime('%Y-%m-%d') + ' 23:59:59'        
#                    cr.execute("SELECT id FROM delivery_time WHERE type='dts' AND active=True AND start_date>='" + min_date + "' AND start_date<='" + max_date + "'")
#                    delivery_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
#                elif arg[0] == 'dts_id':
#                    has_dts_set = [(arg[0],arg[1],arg[2])]
#        fold = {}
#        
#        if has_dts_set:
#            delivery_ids2 = delivery_obj.search(cr, uid, has_dts_set)
#            if delivery_ids2:
#                for id in delivery_ids:
#                    if id not in delivery_ids2:
#                        fold[id] = True
#                delivery_ids.extend(delivery_ids2)
#        result = delivery_obj.name_get(cr, uid, delivery_ids, context=context)
#        return result, fold
#    
#    _group_by_full = {
#        'dts_id': _read_group_dts_ids,
#    }
stock_picking_out()


class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _name = "stock.picking.in"
    
    def _get_is_collected(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for pick in self.browse(cr, uid, ids):
            result[pick.id] = pick.purchase_id and pick.purchase_id.is_collected or False
        return result
    
    def _pick_to_update_after_po_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('stock.picking.in').search(cr, uid, [('purchase_id', 'in', ids),('type','=','in')]) or []
    
    _store_is_collected = {
        'stock.picking': (lambda self, cr, uid, ids, context: ids, ['purchase_id'], 10),
        'purchase.order': (_pick_to_update_after_po_change, ['is_collected'], 10),
    }
    
    _columns = {
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', help='Delivery time or turn to receive', domain=[('type', '=', 'dts')]),
        'pts_id':   fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts')]),
        'delivery_state': fields.selection([("not_planned", _("Not yet planned for delivery")), ("planned", _("Planned for delivery")), ("in_del", _("In delivery")), ("del_ok", _("Delivered")), ("del_ex", _("Delivered with exception")), ("del_rt", _("Delivered and returned")), ("del_rt_exp", _("Returned, no delivery"))], 'Delivery State'),
        'carrier_id': fields.many2one('delivery.carrier', 'Carrier'),
        'is_collected': fields.function(_get_is_collected, type='boolean', multi=False, store=_store_is_collected, string='Is Collected'),
    }
    _defaults = {
        'delivery_state': "not_planned",
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order='name', context=None, count=False):
        context = context or {}
        new_args = []
        if 'update_pts' in context and len(args) > 1:
            for arg in args:
                if arg[0] != 'id':
                    new_args.append(arg)
        else:
            new_args = args
        return super(stock_picking_in, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
    
#    def _read_group_dts_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
#        context = context or {}
#        domain  = domain or []
#        delivery_ids  = []
#        delivery_ids2 = []
#        has_dts_set   = False
#        delivery_obj = self.pool.get('delivery.time')
#        if domain:
#            for arg in domain:
#                if arg[0] == 'dts_id.start_date':
#                    min_date = datetime.now().strftime('%Y-%m-%d') + ' 00:00:00'
#                    #max_date = datetime.now() + timedelta(days=1)
#                    max_date = datetime.now().strftime('%Y-%m-%d') + ' 23:59:59'        
#                    cr.execute("SELECT id FROM delivery_time WHERE type='dts' AND active=True AND start_date>='" + min_date + "' AND start_date<='" + max_date + "'")
#                    delivery_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
#                elif arg[0] == 'dts_id':
#                    has_dts_set = [(arg[0],arg[1],arg[2])]
#        fold = {}
#        
#        if has_dts_set:
#            delivery_ids2 = delivery_obj.search(cr, uid, has_dts_set)
#            if delivery_ids2:
#                for id in delivery_ids:
#                    if id not in delivery_ids2:
#                        fold[id] = True
#                delivery_ids.extend(delivery_ids2)
#        result = delivery_obj.name_get(cr, uid, delivery_ids, context=context)
#        return result, fold
#    
#    _group_by_full = {
#        'dts_id': _read_group_dts_ids,
#    }
stock_picking_in()
