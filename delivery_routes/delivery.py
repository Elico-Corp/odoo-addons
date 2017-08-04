# -*- coding: utf-8 -*-
# © 2011 Cubic ERP - Teradata SAC(http://cubicerp.com)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import fields, osv
import time
from datetime import datetime
import pytz
from tools.translate import _
from tools import ustr
import logging
_logger = logging.getLogger(__name__)


class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'so_payment_method': fields.char('Payment Method', size=32),
    }
sale_order()

class delivery_driver(osv.osv):
    _name='delivery.driver'
    
    _columns = {
        'partner_id': fields.many2one('res.partner','Partner',help='Fill this field if the driver is a outsourcing of the company'),
        'employee_id': fields.many2one('hr.employee','Employee',help='Fill this if the driver is a employee of the company'),
        'name': fields.char('Name', size=64, required=True),
        'carrier_id': fields.many2one('delivery.carrier','Carrier'),
        'outsourcing': fields.boolean('Outsourcing ?'),
        'route_ids': fields.one2many('delivery.route','driver_id','Delivery Routes'),
        'is_driver': fields.boolean('Is Driver ?'),
        'is_picker': fields.boolean('Is Picker ?'),
        'active': fields.boolean('Active ?'),
        'color': fields.integer('Color Index'),
        'tmp_route_id': fields.many2one('delivery.route_tmp','Temporary Delivery Route'),
    }
    _defaults = {
        'outsourcing': False,
        'is_driver':   True,
        'active':   True,
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        if type(ids)!=type([]):
            ids = [ids]
        
        if 'tmp_route_id' in vals and 'force_dts_id' in context:
            driver = self.browse(cr, uid, ids[0])
            if vals['tmp_route_id']:
                tmp_route = self.pool.get('delivery.route_tmp').browse(cr, uid, vals['tmp_route_id'])
                if tmp_route.route_id:
                    route_vals = {}
                    if driver.is_driver and not tmp_route.route_id.driver_id:
                        route_vals = {'driver_id':driver.id}
                    elif not tmp_route.route_id.picker_id:
                        route_vals = {'picker_id':driver.id}
                    if route_vals:
                        cr.execute("UPDATE delivery_route SET driver_id = Null WHERE driver_id = " + str(driver.id) + " AND dts_id=" + str(tmp_route.dts_id.id) + " ")
                        cr.execute("UPDATE delivery_route SET picker_id = Null WHERE picker_id = " + str(driver.id) + " AND dts_id=" + str(tmp_route.dts_id.id) + " ")
                        cr.commit()
                        self.pool.get('delivery.route').write(cr, uid, [tmp_route.route_id.id], route_vals)
                    else:
                        raise osv.except_osv(_('Error'), _("You can not assign more than one Deliver and one Picker."))
            else:
                cr.execute("UPDATE delivery_route SET driver_id = Null WHERE driver_id = " + str(driver.id) + " AND dts_id=" + str(context['force_dts_id']) + " ")
                cr.execute("UPDATE delivery_route SET picker_id = Null WHERE picker_id = " + str(driver.id) + " AND dts_id=" + str(context['force_dts_id']) + " ")
                cr.commit()
            
        if 'is_driver' in vals or 'is_picker' in vals:
            driver = self.browse(cr, uid, ids[0])
            is_driver = vals.get('is_driver', driver.is_driver)
            is_picker = vals.get('is_picker', driver.is_picker)
            if is_picker and is_driver:
                vals.update({'color': 8})
            elif is_driver and not is_picker:
                vals.update({'color': 6})
            elif is_picker and not is_driver:
                vals.update({'color': 2})
            else:
                vals.update({'color': 0})
        return super(delivery_driver, self).write(cr, uid, ids, vals, context=context)
    
    def create(self, cr, uid, vals, context=None):
        context = context or {}            
        if 'is_driver' in vals or 'is_picker' in vals:
            is_driver = vals.get('is_driver', False)
            is_picker = vals.get('is_picker', False)
            if is_picker and is_driver:
                vals.update({'color': 8})
            elif is_driver and not is_picker:
                vals.update({'color': 6})
            elif is_picker and not is_driver:
                vals.update({'color': 2})
            else:
                vals.update({'color': 0})
        return super(delivery_driver, self).create(cr, uid, vals, context=context)
    
    
    def search(self, cr, uid, args, offset=0, limit=None, order='name', context=None, count=False):
        onlyactive = True
        for arg in args:
            if len(arg)==3 and arg[0]=='active':
                onlyactive = False
        if onlyactive:
            args.append(('active','=',True))
        return super(delivery_driver, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    
    def _read_group_tmp_route_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        context = context or {}
        route_tmp_obj = self.pool.get('delivery.route_tmp')
        args = []
        if 'force_dts_id' in context:
            args.append(('dts_id', '=', context['force_dts_id']))
        route_tmp_ids = route_tmp_obj.search(cr, uid, args, context=context)
        result = route_tmp_obj.name_get(cr, uid, route_tmp_ids, context=context)
        fold = {}
        return result, fold
    
    _group_by_full = {
        'tmp_route_id': _read_group_tmp_route_ids,
    }
delivery_driver()


class delivery_time_slot(osv.osv):
    _name='delivery.time.slot'
    _columns = {
        'sequence':   fields.integer('Sequence'),
        'name':       fields.char('Name', size=64, required=True),
        'max_time':   fields.char('If before', size=5, required=True, help='This time will be used to assign the Time Slot. Format: 20:30'),
        'start_time': fields.char('From', size=5),
        'end_time':   fields.char('To', size=5),
        'type':       fields.selection([('dts', 'Delivery'), ('pts', 'Preparation')], 'Type', required=True, select=True),
        'parent_id':  fields.many2one('delivery.time.slot','Parent'),
        'dts_id':     fields.many2one('delivery.time.slot','Linked Delivery Time', domain=[('type','=','dts')]),
        'shop_id':    fields.many2one('sale.shop','Shop'),
    }
    _defaults = {
        'type': 'dts',
        'max_time': '20:30',
    }
    _order = 'sequence, name DESC'
delivery_time_slot()


class delivery_time(osv.osv):
    _name='delivery.time'
    
    _columns = {
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name', size=64, required=True),
        #'start_hour': fields.selection(([(str(x),str(x)) for x in range(0,24)] + [('-','--')]),'Start Hour'),
        #'start_minute': fields.selection(([(str(x*5),str(x*5)) for x in range(0,12)] + [('-','--')]),'Start Minute'),
        #'end_hour': fields.selection(([(str(x),str(x)) for x in range(0,24)] + [('-','--')]),'End Hour'),
        #'end_minute': fields.selection(([(str(x*5),str(x*5)) for x in range(0,12)] + [('-','--')]),'End Minute'),
        'start_date': fields.datetime('Delivery Time From'),
        'end_date': fields.datetime('Delivery Time To'),
        'active': fields.boolean('Active'),
        'type': fields.selection([('dts', 'Delivery'), ('pts', 'Preparation')], 'Type', required=True, select=True),
        'dts_id':    fields.many2one('delivery.time','Linked Delivery Time', domain=[('type','=','dts')]),
        'slot_id':   fields.many2one('delivery.time.slot','Time Slot'),
    }
    _defaults = {
        'active': True,
        'type': 'dts',
    }


    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if context is None:
            context = {}
        if not args:
            args = []
        args.extend(context.get('domain',[]))
        #ids = self.search(cr, user, args, limit=limit, context=context)
        #return self.name_get(cr, user, ids, context)
        return super(delivery_time, self).name_search(cr, user, name, args=args, operator=operator, context=context, limit=limit)

    def create_from_time(self, cr, uid, data, context=None):
        """ create a delivery.time by given time
        start_date:
        end_date:
        """
        #start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
        #end_date = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S')
        context_tz = context.get('tz', 'Asia/Shanghai')
        tz = pytz.timezone(context_tz)
        start = pytz.utc.localize(data['start_date']).astimezone(tz)     
        end = pytz.utc.localize(data['end_date']).astimezone(tz)     
        start = start.strftime('%y/%m/%d %H:%M')
        end = end.strftime('%H:%M')
        # convert start in user's timezone
        name = "%s~%s" %(start,end,)
        data.update({'name':name})
        return self.create(cr, uid, data, context)

    _order = 'sequence, name DESC'
delivery_time()


class delivery_carrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"

    _columns = {
        'driver_ids' : fields.one2many('delivery.driver','carrier_id','Delivery Drivers'),
    }
delivery_carrier()


class delivery_route_tmp(osv.osv):
    _name = 'delivery.route_tmp'
    
    _columns = {
        'name': fields.char('Reference', size=64, required=False),
        'dts_id': fields.many2one('delivery.time','Delivery Time', select=True, domain=[('type','=','dts')]),
        'route_id': fields.many2one('delivery.route','Route', required=False),
    }
delivery_route_tmp()


class delivery_route(osv.osv):
    _name='delivery.route'
    
    def _init_name(self, cr, uid, context=None):
        context = context or {}
        dts_id = context.get('force_dts_id_kanban', False) or False
        if dts_id:
            dts_pool = self.pool.get('delivery.time')
            base_name = dts_pool.read(cr, uid, [dts_id], ['name'])[0]['name'].split()[0]
            for idx in range(1,99):
                name = base_name + str(idx).rjust(2, '0')
                ids = self.search(cr, uid, [('name','ilike',name)]) or False
                if not ids:
                    return name
        return '/'
    
    
    def name_get(self, cr, uid, ids, context=None):
        context = context or {}
        result  = []
        if isinstance(ids, int):
            ids = [ids]
        
        if context.get('force_dts_id_kanban', False):
            for record in self.browse(cr, uid, ids, context=context):
                name = ustr(record.name)
                if record.driver_id:
                    name = ustr(record.driver_id.name)+' '+name[2:]
                result.append((record.id, name.strip()))
        else:
            for record in self.browse(cr, uid, ids, context=context):
                result.append((record.id, record.name.strip()))
        return result
    
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'delivery.route'
            # SHOULD USE ir_sequence.next_by_code() or ir_sequence.next_by_id()
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(delivery_route, self).create(cr, user, vals, context)
        return new_id
    
    _columns = {
        'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', required=False, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'dts_id': fields.many2one('delivery.time','Delivery Time', select=True, domain=[('type','=','dts')], readonly=True, states={'draft': [('readonly', False)]}),
        'driver_id': fields.many2one('delivery.driver','Delivery Driver', required=False, domain=[('is_driver','=',True)], readonly=True, states={'draft': [('readonly', False)]}),
        'picker_id': fields.many2one('delivery.driver','Delivery Deliver', required=False, domain=[('is_picker','=',True)], readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
                            ('draft','Draft'),
                            ('confirm','Confirm'),
                            ('departure','Departure'),
                            ('done', 'Done'),
                            ('cancel','Cancel')],'State',readonly=True),
        'line_ids': fields.one2many('delivery.route.line','route_id','Lines', required=True, readonly=False, states={'done': [('readonly', True)]}),
        'departure_date': fields.datetime('Departure Date', readonly=False, states={'done': [('readonly', True)]}),
        'arrive_date': fields.datetime('Arrive Date', readonly=False, states={'done': [('readonly', True)]}),
        'confirm_cs': fields.boolean('Confirmed by CS'),
    }
    _defaults = {
        'state': 'draft',
        'name': lambda self, cr, uid, context: self._init_name(cr, uid, context=context),
        'dts_id': lambda self, cr, uid, context: context.get('force_dts_id_kanban', False) or False,
    }
    
    def action_draft(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                line_obj.action_draft(cr,uid,[line.id],context=context)
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True
    
    def action_confirm(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                line_obj.action_confirm(cr,uid,[line.id],context=context)
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True
        
    def action_departure(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            if not route.confirm_cs:
                raise osv.except_osv(_('Error'), _("Before departure, routes need to be confirmed by the Customer Service."))
            for line in route.line_ids:
                line_obj.action_delivered(cr,uid,[line.id],context=context)
        self.write(cr, uid, ids, {'state': 'departure','departure_date':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
        
    def action_arrive(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'arrive'}, context=context)
        return True
        
    def action_done_cs(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'confirm_cs': True}, context=context)
        return True
    
    def action_done(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                if line.state in ('draft','confim','delivered'):
                    raise osv.except_osv(_('Error'), _("All the lines of delivery route must be delivered or returned."))
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True
        
    def action_cancel(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                line_obj.action_cancel(cr,uid,[line.id],context=context)
        self.write(cr, uid, ids, {'state': 'cancel','confirm_cs':False}, context=context)
        return True
    

    def _read_group_driver_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        context = context or {}
        driver_obj = self.pool.get('delivery.driver')
        args = [('is_driver', '=', True)]
        driver_ids = driver_obj.search(cr, uid, args, context=context)
        result = driver_obj.name_get(cr, uid, driver_ids, context=context)
        fold = {}
        return result, fold
    
    def _read_group_picker_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        context = context or {}
        driver_obj = self.pool.get('delivery.driver')
        args = [('is_picker', '=', True)]
        driver_ids = driver_obj.search(cr, uid, args, context=context)
        result = driver_obj.name_get(cr, uid, driver_ids, context=context)
        fold = {}
        return result, fold
    
    _group_by_full = {
        'driver_id': _read_group_driver_ids,
        'picker_id': _read_group_picker_ids,
    }
    _order = 'date DESC, name'
delivery_route()


class delivery_route_line(osv.osv):
    _name='delivery.route.line'
    
    def _get_drivers(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for route in self.browse(cr, uid, ids):
            res = {}
            if route.route_id:
                res['picker'] = route.route_id.picker_id and route.route_id.picker_id.name or " "
                res['driver'] = route.route_id.driver_id and route.route_id.driver_id.name or " "
            else:
                res['picker'] = " "
                res['driver'] = " "
            result[route.id] = res
        return result
    
    
    def _get_origin(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for route in self.browse(cr, uid, ids):
            res = {}
            res['origin'] = route.picking_id.origin or route.picking_id.name or ""
            res['sale_order_id'] = route.picking_id.sale_id and route.picking_id.sale_id.id or False
            res['purchase_id'] = route.picking_id.purchase_id and route.picking_id.purchase_id.id or False
            res['address_id'] = route.picking_id.partner_id and route.picking_id.partner_id.id or False
            res['so_payment_method'] = route.picking_id.sale_id and route.picking_id.sale_id.so_payment_method or False
            res['picking_note'] = route.picking_id.note or " "
            result[route.id] = res
        return result
    
    
    def _get_box_type(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for route in self.browse(cr, uid, ids):
            box_type = ''
            iced  = False
            warm  = False
            other = False
            pack_set = set([move.product_id.deliver_in for move in route.picking_id.move_lines ])
            for pack in pack_set:
                if pack in ['warm', 'iced', 'iced_n_warm'] and not iced:
                    if pack in ['iced', 'iced_n_warm']:
                        box_type += '冷, '
                        iced = True
                    if pack in ['warm', 'iced_n_warm'] and not warm:
                        box_type += '热, '
                        warm = True
                else:
                    if not other:
                        box_type += '正常, '
                        other = True
            if box_type:
                box_type = box_type[:-2]
            res[route.id] = box_type
        return res
    
    
    def _route_to_update_after_picking_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('delivery.route.line').search(cr, uid, [('picking_id','in',ids)]) or []
    
    
    def _route_to_update_after_parent_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('delivery.route.line').search(cr, uid, [('route_id','in',ids)]) or []
    
    
    _store_origin = {
        'delivery.route.line': (lambda self,cr,uid,ids,context: ids,['picking_id'],10), 
        'stock.picking': (_route_to_update_after_picking_change, ['sale_id','purchase_id','origin','note','so_payment_method','partner_id'], 10),
    }
    _store_drivers = {
        'delivery.route.line': (lambda self,cr,uid,ids,context: ids,['route_id'],10), 
        'delivery.route': (_route_to_update_after_parent_change, ['picker_id','driver_id'], 10),
    }
    
    _columns = {
        'sequence': fields.integer('Sequence'),
        'route_id': fields.many2one('delivery.route','Delivery Route', required=False, readonly=True, states={'draft': [('readonly', False)]}, ondelete="cascade"),
        'picking_id': fields.many2one('stock.picking','Picking', required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),            
        'purchase_id': fields.function(_get_origin, type='many2one', obj='purchase.order', store=_store_origin, multi="origin", string='Purchase Order'),
        'sale_order_id': fields.function(_get_origin, type='many2one', obj='sale.order', store=_store_origin, multi="origin", string='Sale Order'),
        'origin': fields.function(_get_origin, type='char', size=256, store=_store_origin, multi="origin", string='Origin'),
        'confirm_cs': fields.related('route_id','confirm_cs',type='boolean',string='Confirmed by CS'),
        'address_id': fields.function(_get_origin,type='many2one',relation='res.partner', multi="origin", string='Delivery Address'),
        'street': fields.related('address_id', 'street', type='char', size=256, string='Street'),
        'partner_phone': fields.related('address_id', 'phone', type='char', size=128, string='Partner Phone', readonly=True),
        'picker': fields.function(_get_drivers, type='char', size=128, store=_store_drivers, multi="drivers", string='Clerk'),
        'driver': fields.function(_get_drivers, type='char', size=128, store=_store_drivers, multi="drivers", string='Driver'),
        'driver_phone': fields.related('route_id', 'driver_id', 'employee_id', 'mobile_phone', type='char', size=128, string='Driver Phone'),
        'so_payment_method': fields.function(_get_origin, type='char', size=128, multi="origin", string='Payment Method'),
        'picking_note': fields.function(_get_origin, type='html', multi="origin", string='DO Notes'),
        'box_type': fields.function(_get_box_type, type='char', size=32, store=False, string='Box Type'),
        'state': fields.selection([('draft','Draft'), ('confirm','Confirm'), ('delivered','In delivery'), ('received','Delivered'), ('returned','Returned'), ('cancel','Cancel')],'State',readonly=True),
        'visit_date': fields.datetime('Visit Date',states={'delivered': [('required', True)], 'received':[('readonly',True)], 'returned':[('readonly',True)],}),
        'note': fields.text('Notes'),
        'color': fields.integer('Color Index'),
        'exceptions': fields.boolean('Received with exceptions'),
        'complete_state': fields.selection([("not_planned", _("Not planned")), ("planned", _("Planned")), ("in_del", _("In delivery")), ("del_ok", _("Delivered")), ("del_ex", _("Exception")), ("del_rt", _("Returned")), ("del_rt_exp", _("No redelivery")), ("cancel", _("Cancel"))], 'Delivery State'),
    }
    _defaults = {
        'state': 'draft',
        'complete_state': 'not_planned',
    }
    _order = 'sequence'


    def _read_group_route_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        context = context or {}
        route_obj = self.pool.get('delivery.route')
        args = [('state', '=', 'draft')]
        if 'force_dts_id_kanban' in context:
            args.append(('dts_id', '=', context['force_dts_id_kanban']))
        route_ids = route_obj.search(cr, uid, args, order='name', context=context)
        result = route_obj.name_get(cr, uid, route_ids, context=context)
        fold = {}
        return result, fold
    
    
    def unlink(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            if o.state not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete Delivery Route Line(s) which are already received, returned or delivered !'))
        return super(delivery_route_line, self).unlink(cr, uid, ids, context=context)

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft','delivery_state':'not_planned'}, context=context)
        return True

    def action_received_do_line(self, cr, uid, line, context=None):
        self.pool.get('stock.picking').write(cr,uid,[line.picking_id.id],{'delivered':True,'delivery_state':'del_ok'}, context=context)
        self.notify_related_order(cr, uid, line, 'The Order has been <b>Delivered</b>', context)
        return True
    
    def action_received_exp_do_line(self, cr, uid, line, context=None):
        self.pool.get('stock.picking').write(cr,uid,[line.picking_id.id],{'delivered':True,'delivery_state':'del_ex'}, context=context)
        self.notify_related_order(cr, uid, line, 'The Order has been <b>Delivered with exceptions</b>', context)
        return True
    
    def action_delivered_do_line(self, cr, uid, line, context=None):
        delivered_cpt = line.picking_id.delivered_cpt + 1
        self.pool.get('stock.picking').write(cr,uid,[line.picking_id.id],{'delivered_cpt':delivered_cpt,'delivery_state':'in_del'}, context=context)
        self.notify_related_order(cr, uid, line, 'The Order is <b>in Delivery</b>', context)
        return True
    
    def action_returned_do_line(self, cr, uid, line, context=None):
        contexet = context or {}
        context.update({'set_dts': False})
        self.pool.get('stock.picking').write(cr,uid,[line.picking_id.id],{'delivery_state':'del_rt'}, context=context)
        #self.copy(cr, uid, line.id, {'dts_id':False,'note': 'Re-delivery for ' + str(line.origin),'route_id':False,'return_reasons':[],'exceptions':False,'state':'draft','complete_state':'not_planned','visit_date':False,'color':0}, context=context)
        self.create(cr, uid, {'dts_id':False,
                              'note': 'Re-delivery for ' + str(line.origin),
                              'route_id':False,
                              'return_reasons':[],
                              'exceptions': False,
                              'color':0,
                              'picking_id':line.picking_id and line.picking_id.id,}, context=context)
        
        self.notify_related_order(cr, uid, line, 'The Order has been <b>Returned (Redelivery)</b>', context)
        return True
    
    def action_returned_exp_do_line(self, cr, uid, line, context=None):
        self.pool.get('stock.picking').write(cr,uid,[line.picking_id.id],{'delivered':True,'delivery_state':'del_rt_exp'}, context=context)
        self.notify_related_order(cr, uid, line, 'The Order has been <b>Returned (No Redelivery)</b>', context)
        return True
        
    def action_delivered(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        for line in self.browse(cr,uid,ids,context=context):
            self.action_delivered_do_line(cr, uid, line, context=context)
        self.write(cr, uid, ids, {'complete_state':'in_del', 'state': 'delivered'}, context=context)
        return True
        
    def action_received(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            self.action_received_do_line(cr, uid, line, context=context)
        self.write(cr, uid, ids, {'complete_state':'del_ok', 'state': 'received','visit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
    
    def action_received_exp(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            self.action_received_exp_do_line(cr, uid, line, context=context)
        self.write(cr, uid, ids, {'complete_state':'del_ex', 'state': 'received', 'exceptions': True,'visit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
        
    def action_returned(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            self.action_returned_do_line(cr, uid, line, context=context)
        self.write(cr, uid, ids, {'complete_state':'del_rt', 'state': 'returned','visit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
    
    def action_returned_exp(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            self.action_returned_exp_do_line(cr, uid, line, context=context)
        self.write(cr, uid, ids, {'complete_state':'del_rt_exp', 'state': 'returned', 'exceptions': True,'visit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
        
    def action_cancel_do_line(self, cr, uid, line, context=None):
        delivered_cpt = line.picking_id.delivered_cpt - 1
        if delivered_cpt < 0:
            delivered_cpt = 0
        self.pool.get('stock.picking').write(cr, uid, line.picking_id.id,{'delivered':False, 'delivered_cpt':delivered_cpt, 'delivery_state':'not_planned'},context=context)
        self.notify_related_order(cr, uid, line, 'The Delivery has been <b>Canceled</b>', context)
        return True
        
    def action_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            self.action_cancel_do_line(cr, uid, line, context=context)
        self.write(cr, uid, ids, {'state': 'cancel', 'complete_state':'cancel', 'exceptions': False}, context=context)
        return True
        
    def action_confirm_do_line(self, cr, uid, line, context=None):
        self.pool.get('stock.picking').write(cr, uid, line.picking_id.id,{'delivery_state':'planned'},context=context)
        self.notify_related_order(cr, uid, line, 'The Delivery has been <b>Planned</b>', context)
        return True
        
    def action_confirm(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            if line.picking_id.delivered:
                raise osv.except_osv(_('Error'), _('The picking %s (origin:%s) was delivered in other delivery route'%(line.picking_id.name,line.picking_id.origin)))
#            if line.picking_id.type == 'out' and line.picking_id.state not in ('done'):
#                raise osv.except_osv(_('Error'), _('The picking %s (origin:%s) must be in done state'%(line.picking_id.name,line.picking_id.origin)))
            self.action_confirm_do_line(cr, uid, line, context=context)
        self.write(cr, uid, ids, {'complete_state':'planned', 'state': 'confirm'}, context=context)
        return True
    
    def notify_related_order(self, cr, uid, line, delivery_state, context=None):
        res_id = False
        model  = False
        
        if line.sale_order_id:
            res_id = line.sale_order_id.id
            model  = 'sale.order'
        elif line.purchase_id:
            res_id = line.purchase_id.id
            model  = 'purchase.order'
        
        if res_id and model:
            drivers = ''
            body = str(delivery_state)
            if line.visit_date:
                body += " at " + str(line.visit_date)
            body += "<br />"
            if line.route_id.name:
                body += "<b>Route</b>: " + str(line.route_id.name) + "<br />"
            if line.route_id.driver_id:
                drivers += str(line.route_id.driver_id.name.encode('utf-8'))
                if line.route_id.driver_id.employee_id and line.route_id.driver_id.employee_id.mobile_phone:
                    drivers += " (" + str(line.route_id.driver_id.employee_id.mobile_phone) + ")"
            if line.route_id.picker_id:
                if drivers:
                    drivers += ' & '
                drivers += str(line.route_id.picker_id.name.encode('utf-8'))
            if drivers:
                body += "by: " + drivers + ")"
            
            self.pool.get('mail.message').create(cr, uid, {
                'type': 'notification',
                'record_name': 'Delivery Route Line',
                'body': body,
                'res_id': res_id,
                'model': model,
            })
        return True
    
    
    _group_by_full = {
        'route_id': _read_group_route_ids,
    }
delivery_route_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
