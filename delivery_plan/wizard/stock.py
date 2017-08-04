# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import threading
from openerp import netsvc
from openerp import pooler
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import pytz
import logging
logger = logging.getLogger(__name__)


class delivery_dts_to_routes(osv.osv_memory):
    _name = 'delivery.dts_to_routes'
    
    def _init_dts_id(self, cr, uid, context=None):
        last_dts = self.pool.get('res.users').read(cr, 1, [uid], ['dts_id'])[0]['dts_id']
        if last_dts:
            ids = self.pool.get('delivery.time').search(cr, uid, [('id', '=', last_dts[0])])
        else:
            now = datetime.now()
            ids = self.pool.get('delivery.time').search(cr, uid, [('type', '=', 'dts'), ('active', '=', True), ('name', 'ilike', datetime.strftime(now, '%y%m%d') + '%')])
        return ids and ids[0] or False

    _columns = {
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', select=True, required=True, domain=[('type', '=', 'dts'), ('active', '=', True)]),
    }
    _defaults = {
        'dts_id': lambda self, cr, uid, context: self._init_dts_id(cr, uid, context=context),
    }
    
    def generate_routes(self, cr, uid, ids, context=None):
        context = context or {}
        route_obj = self.pool.get('delivery.route')
        line_obj = self.pool.get('delivery.route.line')
        
        if ids:
            data = self.browse(cr, uid, ids)[0]
        else:
            data = self.pool.get('delivery.time').browse(cr, 1, context['wiz_dts_id'])
        self.pool.get('res.users').write(cr, 1, [uid], {'dts_id':data.dts_id.id})
        
        color2routes = {}
        line_ids = line_obj.search(cr, uid, [("dts_id", "=", data.dts_id.id)], order="color")
        for line in line_obj.browse(cr, uid, line_ids):
            route_id = False
            base_name = data.dts_id.name.split()[0]
            if line.color > 0:
                line_color = str(line.color).rjust(2, '0')
                if line_color in color2routes:
                    route_id = color2routes[line_color]
                else:
                    route_ids = route_obj.search(cr, uid, [('name', '=', base_name  + str(line_color))], context=context)
                    route_id  = route_ids and route_ids[0] or False
                    color2routes.update({line_color: route_id})
                
                if not route_id:
                    route_id = route_obj.create(cr, uid, {
                        'name': base_name + str(line_color),
                        'date': data.dts_id.start_date and data.dts_id.start_date.split() and data.dts_id.start_date.split()[0] or False,
                        'dts_id': data.dts_id.id,
                        'departure_date': data.dts_id.start_date or False,
                        'arrive_date': data.dts_id.end_date or False,
                    })
                    color2routes.update({line_color: route_id})
                line_obj.write(cr, uid, [line.id], {'route_id':route_id}, context={'force_update':1})
        
        #domain = ['&','|','&',('picking_id.type','=','in'),'&',('picking_id.state','=','assigned'),("picking_id.is_collected","=",True),'&',('picking_id.type','=','out'),("picking_id.state","not in",["cancel"]),'|',("route_id","in",tuple(route_ids)),("route_id","=",None)]
        domain = ['&','|','&',('picking_id.type','=','in'),'&',('picking_id.state','=','assigned'),("picking_id.is_collected","=",True),'&',('picking_id.type','=','out'),("picking_id.state","not in",["cancel"]),("dts_id","=",data.dts_id.id)]
        
        return {
            'type': 'ir.actions.act_window',
            'res_model':'delivery.route.line',
            'view_type':'form',
            'view_mode':'kanban,form',
            'context':"{'update_color':1,'view_name':'delivery.route.line.kanban','force_dts_id_kanban': %s}" % data.dts_id.id,
            'domain': domain,
        }        
delivery_dts_to_routes()


class delivery_dts_to_vans(osv.osv_memory):
    _name = 'delivery.dts_to_vans'
    
    def _init_dts_id(self, cr, uid, context=None):
        last_dts = self.pool.get('res.users').read(cr, 1, [uid], ['dts_id'])[0]['dts_id']
        if last_dts:
            ids = self.pool.get('delivery.time').search(cr, uid, [('id', '=', last_dts[0])])
        else:
            now = datetime.now()
            ids = self.pool.get('delivery.time').search(cr, uid, [('type', '=', 'dts'), ('active', '=', True), ('name', 'ilike', datetime.strftime(now, '%y%m%d') + '%')])
        return ids and ids[0] or False

    _columns = {
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', select=True, required=True, domain=[('type', '=', 'dts'), ('active', '=', True)]),
    }
    _defaults = {
        'dts_id': lambda self, cr, uid, context: self._init_dts_id(cr, uid, context=context),
    }
    
    def open_kanban(self, cr, uid, ids, context=None):
        if ids:
            data = self.browse(cr, uid, ids)[0]
        else:
            data = self.pool.get('delivery.time').browse(cr, 1, context['wiz_dts_id'])
        self.pool.get('res.users').write(cr, 1, [uid], {'dts_id':data.dts_id.id})
        #domain = [("picking_id.state", "!=", "cancel"), ("picking_id.type", "in", ["in", "out"]), ("dts_id", "=", data.dts_id.id)]
        domain = ['&','|','&',('picking_id.type','=','in'),'&',('picking_id.state','=','assigned'),("picking_id.is_collected","=",True),'&',('picking_id.type','=','out'),("picking_id.state","not in",["cancel"]),("dts_id","=",data.dts_id.id)]
        
        return {
            'type': 'ir.actions.act_window',
            'res_model':'delivery.route.line',
            'view_type':'form',
            'view_mode':'kanban,form',
            'context':"{'view_name':'delivery.route.line.kanban_fc','sorting':'neighborhood,street,picking_id','check4color':" + str(data.dts_id.id) + "}",
            'domain': domain,
        }
delivery_dts_to_vans()



class delivery_driver_for_routes(osv.osv_memory):
    _name = 'delivery.driver_for_routes'
    
    def _init_dts_id(self, cr, uid, context=None):
        last_dts = self.pool.get('res.users').read(cr, 1, [uid], ['dts_id'])[0]['dts_id']
        if last_dts:
            ids = self.pool.get('delivery.time').search(cr, uid, [('id', '=', last_dts[0])])
        else:
            now = datetime.now()
            ids = self.pool.get('delivery.time').search(cr, uid, [('type', '=', 'dts'), ('active', '=', True), ('name', 'ilike', datetime.strftime(now, '%y%m%d') + '%')])
        return ids and ids[0] or False

    _columns = {
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', select=True, required=True, domain=[('type', '=', 'dts'), ('active', '=', True)]),
        #'action': fields.selection([('driver_id','Driver'),('picker_id','Deliver')], string="Choose", required=True),
    }
    _defaults = {
        'dts_id': lambda self, cr, uid, context: self._init_dts_id(cr, uid, context=context),
        #'action': lambda *a: 'driver_id',
    }
    
    def open_kanban(self, cr, uid, ids, context=None):
        if ids:        
            data = self.browse(cr, uid, ids)[0]
        else:
            data = self.pool.get('delivery.time').browse(cr, 1, context['wiz_dts_id'])
        self.pool.get('res.users').write(cr, 1, [uid], {'dts_id':data.dts_id.id})
        driver_pool = self.pool.get('delivery.driver')
        route_tmp_pool = self.pool.get('delivery.route_tmp')        
        route_pool = self.pool.get('delivery.route')
        
        #cr.execute("DELETE FROM delivery_route_tmp WHERE dts_id=" + data.dts_id.id + " ")
        cr.execute("DELETE FROM delivery_route_tmp")
        cr.execute("UPDATE delivery_driver SET tmp_route_id = Null")
        cr.commit()
        
        route_ids = route_pool.search(cr, uid, [('dts_id', '=', data.dts_id.id)]) or []
        for route in route_pool.browse(cr, uid, route_ids):
            route_tmp_id = route_tmp_pool.create(cr, uid, {'dts_id': data.dts_id.id, 'route_id': route.id, 'name': route.name})
            if route.driver_id:
                driver_pool.write(cr, uid, [route.driver_id.id], {'tmp_route_id': route_tmp_id})
            if route.picker_id:
                driver_pool.write(cr, uid, [route.picker_id.id], {'tmp_route_id': route_tmp_id})        
        
        return {
            'type': 'ir.actions.act_window',
            'res_model':'delivery.driver',
            'view_type':'tree',
            'view_mode':'kanban',
            'context':"{'force_dts_id': %s}" % (data.dts_id.id),
        }    
delivery_driver_for_routes()


class delivery_change_dts(osv.osv_memory):
    _name = 'delivery.change.dts'
    _description = 'Change DTS / PTS'
    
    _columns = {
        'action': fields.selection([('cleanup', 'Blank DTS/PTS'), ('change', 'Change DTS/PTS')], string='Action', required=True),
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', domain=[('type', '=', 'dts')]),
        'pts_id': fields.many2one('delivery.time', 'Preparation Time', domain=[('type', '=', 'pts')]),
    }
    _defaults = {
        'action': 'change',
    }
    
    
    def dts_id_change(self, cr, uid, ids, dts_id, pts_id, context=None):
        context = context or {}
        new_pts_id = False
        
        if pts_id and dts_id:
            pts_pool = self.pool.get('delivery.time')
            pts = pts_pool.browse(cr, uid, [pts_id])[0]
            if pts.dts_id.id == dts_id:
                new_pts_id = pts_id           
        return {'value': {'pts_id': new_pts_id}}
    
    
    def change_dts(self, cr, uid, ids, context=None):
        context = context or {}
        context.update({'update_pts':1})
        pick_ids = context.get('active_ids', False) or context.get('active_id', False) or []
        if pick_ids and type(pick_ids) != type([]):
            pick_ids = [pick_ids]
        
        if pick_ids:
            move_pool = self.pool.get('stock.move')
            pick_pool = self.pool.get('stock.picking')
            this = self.browse(cr, uid, ids[0], context=context)
            
            if this.action == 'cleanup':
                pts_id = False
                dts_id = False
            else:
                dts_id = this.dts_id and this.dts_id.id or False
                if dts_id:
                    pts_id = this.pts_id and this.pts_id.id or False
                else:
                    pts_id = False
            
            for pick in pick_pool.browse(cr, uid, pick_ids):
                if pick.state not in ['cancel'] and pick.delivery_state in ["not_planned", "del_rt", ""]:
                    pick_pool.write(cr, uid, [pick.id], {'pts_id':pts_id, 'dts_id':dts_id}, context=context)
        return {'type': 'ir.actions.act_window_close'}

delivery_change_dts()



########## TO BE DELETED ASAP ###############
class dts_reset(osv.osv):
    _name = 'dts.reset'
    
    def resetall(self, cursor, uid, context=None):
        logger.warning('################ START ################')
        picking_obj  = self.pool.get('stock.picking')
        delivery_obj = self.pool.get('delivery.route.line')
        
        cr2 = pooler.get_db(cursor.dbname).cursor()
        cr2.execute("SELECT DISTINCT picking_id FROM delivery_route_line WHERE picking_id is not null")
        pick_ids    = map(lambda x: x[0], cr2.fetchall())
        picking_ids =  picking_obj.search(cr2, uid, [('id','not in',pick_ids),('state','not in',['cancel']),('type','in',['in','out'])])
        for sp in picking_ids:
            delivery_obj.create(cr2, uid, {'picking_id':sp, })
            cr2.commit()
            logger.warning('####  %s done  #### '%sp)
        #cancel picking canceled
        logger.warning('################ DONE ################')
        cr2.close()
        
        """
        logger.warning('################ START ################')
        tz = pytz.timezone('Asia/Shanghai')
        tz2 = pytz.timezone('America/Anchorage')
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        delivery_time_obj = self.pool.get('delivery.time')
        time_slot_obj = self.pool.get('delivery.time.slot')
        so_pool = self.pool.get('sale.order')
        
        use_new_cursor = cursor.dbname
        cr = pooler.get_db(use_new_cursor).cursor()
        cr2 = pooler.get_db(use_new_cursor).cursor()
        cr3 = pooler.get_db(use_new_cursor).cursor()
        
        cr2.execute("SELECT DISTINCT sale_id FROM stock_picking WHERE sale_id is not null AND sale_id > 0")
        ids_from_pick = map(lambda x: x[0], cr2.fetchall())
        so_ids = so_pool.search(cr3, uid, [('id','not in',ids_from_pick)])
        
        cpt_commit = 1
        for order in so_pool.browse(cr3, uid, so_ids):
            val = {}
            dts = False
            pts = False
            pt_id = False
            dt_id = False
            min_date = False
            slot_id = False
            
            try:
                now = datetime.now()
                address = order.partner_shipping_id or order.partner_id or False
                
                if order.start_date:
                    min_date = order.start_date
                    dts = order.start_date
                    dts = datetime.strptime(dts, '%Y-%m-%d %H:%M:%S')            
                    dts = pytz.utc.localize(dts).astimezone(tz)
                if order.cdate:
                    pts = datetime.strptime(order.cdate, '%Y-%m-%d %H:%M:%S')
                    pts = pytz.utc.localize(pts).astimezone(tz)
                elif order.date_order:
                    pts = datetime.strptime(order.date_order, '%Y-%m-%d')
                    pts = pytz.utc.localize(pts).astimezone(tz)
                if not pts:
                    pts = dts
                
                if dts:
                    start_date = datetime.strftime(dts, '%Y-%m-%d')
                    if address and (not address.city or address.city.lower() in ['shanghai']):
                        from_time = datetime.strftime(dts, '%H:%M')
                    else:#eg: in Nanjing
                        from_time = '09:30'
                    name = datetime.strftime(dts, '%y%m%d')
                    name_pts = name
                    start_date_pts = start_date
                    
                    slot_ids = time_slot_obj.search(cr, uid, [('max_time', '>=', from_time), ('type', '=', 'dts')], order='max_time')
                    if slot_ids:
                        slot = time_slot_obj.browse(cr, uid, slot_ids[0])
                        name += slot.name
                        end_date = start_date + ' ' + slot.end_time
                        start_date += ' ' + slot.start_time
                        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
                        start_date = pytz.utc.localize(start_date).astimezone(tz2)
                        start_date = datetime.strftime(start_date, '%Y-%m-%d %H:%M')
                        end_date   = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
                        end_date   = pytz.utc.localize(end_date).astimezone(tz2)
                        end_date   = datetime.strftime(end_date, '%Y-%m-%d %H:%M')
                        
                        cr2.execute("SELECT id FROM delivery_time WHERE name='" + name + "' AND type='dts' AND slot_id='" + str(slot.id) + "'")
                        dt_ids = map(lambda x: x[0], cr2.fetchall())
                        if dt_ids:
                            dt_id = dt_ids[0]
                        else:
                            dt_id = delivery_time_obj.create(cr3, uid, {
                                'name':name,
                                'start_date': start_date,
                                'end_date': end_date,
                                'active': True,
                                'type': 'dts',
                                'slot_id': slot.id,
                                }, context)
                            cr3.commit()
                            cr2.commit()
                
                if pts and dt_id:
                    date_pts = datetime.strftime(pts, '%Y-%m-%d')
                    from_time = datetime.strftime(pts, '%H:%M')
                    if date_pts < datetime.strftime(dts, '%Y-%m-%d'):
                        date_pts = datetime.strftime(dts, '%Y-%m-%d')
                        from_time = '00:00'
                    
                    pts_slot_ids = time_slot_obj.search(cr, uid, [('max_time', '>=', from_time), ('type', '=', 'pts'), ('dts_id', '=', slot.id)], order='max_time')
                    if pts_slot_ids:
                        pts_slot = time_slot_obj.browse(cr, uid, pts_slot_ids[0])
                        name_pts += pts_slot.name
                        end_date_pts = start_date_pts + ' ' + pts_slot.end_time
                        start_date_pts += ' ' + pts_slot.start_time
                        start_date_pts = datetime.strptime(start_date_pts, '%Y-%m-%d %H:%M')
                        start_date_pts = pytz.utc.localize(start_date_pts).astimezone(tz2)
                        start_date_pts = datetime.strftime(start_date_pts, '%Y-%m-%d %H:%M')
                        end_date_pts   = datetime.strptime(end_date_pts, '%Y-%m-%d %H:%M')
                        end_date_pts   = pytz.utc.localize(end_date_pts).astimezone(tz2)
                        end_date_pts   = datetime.strftime(end_date_pts, '%Y-%m-%d %H:%M')
                    
                        cr2.execute("SELECT id FROM delivery_time WHERE name='" + name_pts + "' AND type='pts' AND slot_id='" + str(pts_slot.id) + "'")
                        pt_ids = map(lambda x: x[0], cr2.fetchall())
                        if pt_ids:
                            pt_id = pt_ids[0]
                        else:
                            pt_id = delivery_time_obj.create(cr3, uid, {
                                'name':name_pts,
                                'start_date': start_date_pts,
                                'end_date': end_date_pts,
                                'active': True,
                                'type': 'pts',
                                'slot_id': pts_slot.id,
                                'dts_id': dt_id,
                                }, context)
                            cr3.commit()
                            cr2.commit()
                        val['pts_id'] = pt_id
                if not pt_id:
                    val['pts_id'] = False
                if not dt_id:
                    val['dts_id'] = False
                
                if val:
                    so_pool.write(cr2, 1, [order.id], val)
                
                ##################################################
                #cr2.execute("SELECT DISTINCT id FROM stock_picking WHERE sale_id = "+ str(order.id) +"")
                #pick_ids = map(lambda x: x[0], cr2.fetchall()) or []
                #if pick_ids and val:
                #    picking_obj.write(cr2, uid, pick_ids, val)
                ##################################################
                
                cpt_commit += 1
                if cpt_commit >= 30:
                    cr2.commit()
                    cr3.commit()
                    cr.commit()
                    cpt_commit = 1
            except Exception as err:
                logger.warning('>>> Error during SO %s : %s' % (order.id, err))
        ##################################################
        # We update the old wrong start_date and end_date in delivery.time
        #delivery_time_obj = self.pool.get('delivery.time')
        #cr.execute("SELECT id FROM delivery_time WHERE id<16613 and start_date is not null and end_date is not null")
        #delivery_ids = map(lambda x: x[0], cr.fetchall()) or []
        #for delivery in delivery_time_obj.browse(cr, 1, delivery_ids):
        #    delivery_start = datetime.strptime(delivery.start_date, '%Y-%m-%d %H:%M:%S')
        #    delivery_start = pytz.utc.localize(delivery_start).astimezone(tz2)
        #    
        #    delivery_end   = datetime.strptime(delivery.end_date, '%Y-%m-%d %H:%M:%S')
        #    delivery_end   = pytz.utc.localize(delivery_end).astimezone(tz2)
        #
        #    delivery_time_obj.write(cr2, 1, [delivery.id], {'start_date':delivery_start,'end_date':delivery_end})
        #    cr2.commit()
        ##################################################
        cr.close()
        cr2.close()
        cr3.close()
        logger.warning('################ DONE ################')
        """
        return
dts_reset()

class delivery_reset(osv.osv_memory):
    _name = 'delivery.reset'
    
    def go(self, cr, uid, ids, context=None):
        context = context or {}
        use_new_cursor = cr.dbname
        threaded_calculation = threading.Thread(target=self.pool.get('dts.reset').resetall, args=(cr, uid, context))
        threaded_calculation.start()
        return {'type': 'ir.actions.act_window_close'}
delivery_reset()

#class add_picking_pack(osv.osv_memory):
#    _name='add.picking.pack'
#
#    _columns = {
#            }
#
#    def confirm_add(self, cr, uid, ids, context=None):
#        picking_ids = context['active_ids']
#        
#        sequence_obj = self.pool.get('ir.sequence')
#        picking_obj = self.pool.get('stock.picking')
#        move_obj = self.pool.get('stock.move')
#        ul_obj = self.pool.get('product.ul')
#        batch_obj = self.pool.get('picking.batch')
#        tracking_obj = self.pool.get('stock.tracking')
#
#        batch_id = batch_obj.create(cr, uid, {
#            'name': sequence_obj.get(cr, uid, 'picking.batch')
#            },context=context)
#
#        for picking in picking_obj.browse(cr, uid, picking_ids, context):
#            picking_obj.write(cr, uid, [picking.id,], {'batch_id':batch_id})
#            for line in picking.move_lines :
#                tracking_ids = tracking_obj.search(cr, uid, [
#                    ('picking_id','=',picking.id),
#                    ('ul_id','=',line.product_id.ul_id and line.product_id.ul_id.id or False)],context=context)
#                if tracking_ids :
#                    tracking_id = tracking_ids[0]
#                else:
#                    tracking_id = tracking_obj.create(cr, uid, {
#                        'name':'%s_%s' % (picking.name,line.product_id.ul_id.name),
#                        'picking_id':picking.id,
#                        'ul_id':line.product_id.ul_id and line.product_id.ul_id.id or False,
#                        },
#                        context=context)
#                move_obj.write(cr, uid,[line.id], {'tracking_id':tracking_id},context=context)
#
#        return {
#                'type': 'ir.actions.act_window_close',
#                }
#
#add_picking_pack()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: