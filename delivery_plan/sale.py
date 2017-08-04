# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from openerp import netsvc
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def _get_dts_id(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for so in self.browse(cr, uid, ids, context=context):
            result[so.id] = so.pts_id and so.pts_id.dts_id and so.pts_id.dts_id.id or False
        return result
        
    def _so_to_update_after_dts_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('sale.order').search(cr, uid, [('pts_id', 'in', ids)]) or []
    
    _store_dts_id = {
        'sale.order': (lambda self, cr, uid, ids, context: ids, ['pts_id'], 10),
        'delivery.time': (_so_to_update_after_dts_change, ['dts_id'], 10),
    }    
    
    _columns = {
        'pts_id':   fields.many2one('delivery.time', 'Preparation Time', domain=[('type', '=', 'pts')]),
        'dts_id':  fields.function(_get_dts_id, method=True, type='many2one', relation='delivery.time', string='Delivery Time', store=_store_dts_id, readonly=True, domain=[('type', '=', 'dts')]),
        'batch_id': fields.many2one('picking.batch', 'Picking Batch', change_default=True),
        'start_date': fields.datetime('Delivery Start Date'),
        'end_date': fields.datetime(' Delivery End Date'),
        # 'so_payment_method': fields.char('Payment Method', size=32),
    }

    
    def action_cancel_order_with_moves_not_delivered(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        drl_obj = self.pool.get('delivery.route.line')
        #proc_obj = self.pool.get('procurement.order')
        for sale in self.browse(cr, uid, ids, context=context):
            try:
                for pick in sale.picking_ids:
                    for mov in pick.move_lines:
                        if mov.state not in ('done','cancel'):
                            mov.write({'state':'cancel'})
                                    
                for pick in sale.picking_ids:
                    if pick.state != 'cancel':
                        #wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
                        pick.write({'state':'cancel'})
                for inv in sale.invoice_ids:
                    wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
                for line in sale.order_line:
                    if line.procurement_id:
                        wf_service.trg_validate(uid, 'procurement.order', line.procurement_id.id, 'button_check', cr)
                
                #cancel delivery route line
                drl_ids = drl_obj.search(cr, uid, [('sale_order_id','=',sale.id),('state','!=','cancel')])
                drl_obj.action_cancel(cr,uid,drl_ids,context=context)
                
                order_ref = context.get('order_ref',False)
                self.write(cr, uid, [sale.id], {'state':'shipping_except','client_order_ref':order_ref})
                cr.commit()
            except:
                _logger.info('==== #LY action_cancel_order_with_moves_not_delivered fail %s===='%(sale.id))
        return True
    
    def action_cancel_order_with_moves(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        drl_obj = self.pool.get('delivery.route.line')
        #proc_obj = self.pool.get('procurement.order')
        for sale in self.browse(cr, uid, ids, context=context):
            try:
                if sale.state == 'done':
                        return False
                for pick in sale.picking_ids:
                    if pick.state == 'done':
                        return False
                    for mov in pick.move_lines:
                        if mov.state == 'done':
                            return False
                for inv in sale.invoice_ids:
                    if inv.state == 'paid':
                        return False
                    
                for pick in sale.picking_ids:
                    wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
                for pick in sale.picking_ids:
                    if pick.state != 'cancel':
                        wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
                                    
                for inv in sale.invoice_ids:
                    wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
                for line in sale.order_line:
                    if line.procurement_id:
                        wf_service.trg_validate(uid, 'procurement.order', line.procurement_id.id, 'button_check', cr)
                
                #cancel delivery route line
                drl_ids = drl_obj.search(cr, uid, [('sale_order_id','=',sale.id),('state','!=','cancel')])
                drl_obj.action_cancel(cr,uid,drl_ids,context=context)
                
                sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line], {'state': 'cancel'})
                self.write(cr, uid, [sale.id], {'state': 'cancel'})
                cr.commit()
            except:
                _logger.info('==== #LY action_cancel_order_with_moves fail %s===='%(sale.id))
        return True

    def _prepare_order_line_procurement(self, cr, uid, order, pt_id, line, move_id, date_planned, context=None):
        return {
            'name': line.name,
            'origin': order.name,
            'date_planned': date_planned,
            'product_id': line.product_id.id,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
            'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
            'procure_method': line.type,
            'move_id': move_id,
            'company_id': order.company_id.id,
            'note': line.name,
            'pts_id': pt_id,
        }
    
    def _prepare_order_line_move_fc(self, cr, uid, order, line, picking_id, pt_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0,
            'pts_id':pt_id,
        }
    
    def _prepare_order_picking(self, cr, uid, order, dt_id, pt_id, context=None):
        # SHOULD USE ir_sequence.next_by_code() or ir_sequence.next_by_id()
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': order.date_order,
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy == 'picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
            'dts_id':dt_id,
            'pts_id':pt_id,
        }
    
    def _prepare_pts_dts(self, cr, uid, order, context=None):
        if not context:
            context = {}
        tz = pytz.timezone('Asia/Shanghai')
        tz2 = pytz.timezone('America/Anchorage')
        delivery_time_obj = self.pool.get('delivery.time')
        time_slot_obj = self.pool.get('delivery.time.slot')
        val={}
        
        dts = False
        pts = False
        pt_id = False
        dt_id = False
        min_date = False
        slot_id = False
        now = datetime.now()
        address = order.partner_shipping_id or order.partner_id or False
        
        if order.start_date:
            min_date = order.start_date
            dts = order.start_date
            dts = datetime.strptime(dts, '%Y-%m-%d %H:%M:%S')            
            dts = pytz.utc.localize(dts).astimezone(tz)
        if order.date_order:
            pts = datetime.strptime(order.date_order, '%Y-%m-%d')
            pts = pytz.utc.localize(pts).astimezone(tz)
        if not pts:
            pts = dts
        
        if dts:
            start_date = datetime.strftime(dts, '%Y-%m-%d')
            from_time = datetime.strftime(dts, '%H:%M')
            #LY remove the shanghai restrict out
            # if address and (not address.city or address.city.lower() in ['shanghai']):
            #     from_time = datetime.strftime(dts, '%H:%M')
            # else:  # eg: in Nanjing
            #     from_time = '09:30'
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
                end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
                end_date = pytz.utc.localize(end_date).astimezone(tz2)
                end_date = datetime.strftime(end_date, '%Y-%m-%d %H:%M')
                
                dt_ids = delivery_time_obj.search(cr, uid, [('name', '=', name), ('type', '=', 'dts'), ('slot_id', '=', slot.id)])
                if dt_ids:
                    dt_id = dt_ids[0]
                else:
                    dt_id = delivery_time_obj.create(cr, uid, {
                        'name':name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'active': True,
                        'type': 'dts',
                        'slot_id': slot.id,
                        }, context)
                    cr.commit()
        
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
                end_date_pts = datetime.strptime(end_date_pts, '%Y-%m-%d %H:%M')
                end_date_pts = pytz.utc.localize(end_date_pts).astimezone(tz2)
                end_date_pts = datetime.strftime(end_date_pts, '%Y-%m-%d %H:%M')
            
                pt_ids = delivery_time_obj.search(cr, uid, [('name', '=', name_pts), ('type', '=', 'pts'), ('slot_id', '=', pts_slot.id)])
                if pt_ids:
                    pt_id = pt_ids[0]
                else:
                    pt_id = delivery_time_obj.create(cr, uid, {
                        'name':name_pts,
                        'start_date': start_date_pts,
                        'end_date': end_date_pts,
                        'active': True,
                        'type': 'pts',
                        'slot_id': pts_slot.id,
                        'dts_id': dt_id,
                        }, context)
                    cr.commit()
                val['pts_id'] = pt_id
        if val:
            order.write(val)
        return min_date, dt_id, pt_id
    
    
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: sales order to which the order lines belong
        :param list(browse_record) order_lines: sales order line records to procure
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if ommitted.
        :return: True
        """
        val = {}
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []
        
        min_date, dt_id, pt_id = self._prepare_pts_dts(cr, uid, order)
        # min_date, dt_id, pt_id = order.date_order, order.dts_id.id, order.pts_id.id
        print '<<<<<<<<<<<<<<  %s, %s, %s' % (min_date, dt_id, pt_id)
        
        for line in order_lines:
            if line.state == 'done':
                continue

            date_planned = min_date or self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

            if line.product_id:
                if line.product_id.type in ('product', 'consu'):
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, dt_id, pt_id, context=context))
                    move_id = move_obj.create(cr, uid, self._prepare_order_line_move_fc(cr, uid, order, line, picking_id, pt_id, date_planned, context=context))
                else:
                    # a service has no stock move
                    move_id = False

                proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, pt_id, line, move_id, date_planned, context=context))
                proc_ids.append(proc_id)
                line.write({'procurement_id': proc_id})
                self.ship_recreate(cr, uid, order, line, move_id, proc_id)

        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
        
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False

            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True

sale_order()


class picking_batch(osv.osv):
    _name = "picking.batch"
    _columns = {
        'name': fields.char('Name', size=32, translate=True),
        'picking_ids': fields.one2many('stock.picking', 'batch_id', 'Contains'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }

picking_batch()


class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _columns = {
        'batch_id': fields.many2one('picking.batch', 'Picking Batch', change_default=True),
        'route_line_id': fields.one2many('delivery.route.line', 'picking_id', 'Delivery Time'),
        'so_payment_method': fields.char('Payment Method', size=32),
    }
        
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        pts_id = False
        if type(ids) != type([]):
            ids = [ids]
        if 'dts_id' in vals:
            move_pool = self.pool.get('stock.move')
            proc_pool = self.pool.get('procurement.order')
            pts_pool = self.pool.get('delivery.time')
            drl_pool = self.pool.get('delivery.route.line')
            
            if 'pts_id' not in vals:
                pts_id = pts_pool.search(cr, uid, [('active', '=', True), ('type', '=', 'pts'), ('dts_id', '=', vals['dts_id'])], order='start_date DESC')
                if pts_id:
                    pts_id = pts_id[0]
                    vals.update({'pts_id':pts_id})
            else:
                pts_id = vals['pts_id']
            
            if pts_id:
                move_ids = move_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('picking_id', 'in', ids)])
                if move_ids:
                    move_pool.write(cr, uid, move_ids, {'pts_id':pts_id})
                    proc_ids = proc_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('move_id', 'in', move_ids)])
                    if proc_ids:
                        proc_pool.write(cr, uid, proc_ids, {'pts_id':pts_id})
            
#            Actually DONE in fields.function
#            route_lines = drl_pool.search(cr, uid, [('state', 'in', ['draft']), ('picking_id', 'in', ids)])
#            if route_lines:
#                drl_pool.write(cr, uid, route_lines, {'dts_id': vals['dts_id']})
        return super(stock_picking, self).write(cr, uid, ids, vals, context=context)
    
    
    def pts_id_change(self, cr, uid, ids, pts_id, context=None):
        res = {}
        context = context or {}
        if type(ids) != type([]):
            ids = [ids]
        move_pool = self.pool.get('stock.move')
        proc_pool = self.pool.get('procurement.order')
        pts_pool = self.pool.get('delivery.time')
        drl_pool = self.pool.get('delivery.route.line')
        
        if pts_id:
            pts = pts_pool.browse(cr, uid, [pts_id])[0]
            #self.write(cr, uid, ids, {'dts_id':pts and pts.dts_id and pts.dts_id.id or False})
            res['dts_id'] = pts and pts.dts_id and pts.dts_id.id or False
        
        move_ids = move_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('picking_id', 'in', ids)])
        if move_ids:
            vals = {'pts_id':pts_id}
            if pts_id:
                vals.update({'date_expected':pts.dts_id.start_date})
            move_pool.write(cr, uid, move_ids, vals)
            proc_ids = proc_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('move_id', 'in', move_ids)])
            if proc_ids:
                proc_pool.write(cr, uid, proc_ids, {'pts_id':pts_id})
        
#        Actually DONE in fields.function
#        route_lines = drl_pool.search(cr, uid, [('state', 'in', ['draft']), ('picking_id', 'in', ids)])
#        if route_lines and 'dts_id' in res:
#            drl_pool.write(cr, uid, route_lines, {'dts_id': res['dts_id']})
        return {'value': res}


    def create(self, cr, uid, data, context=None):
        """
        create route line 
        """
        if not data.get('pts_id', False) and data.get('origin', False):
            so_obj = self.pool.get('sale.order')
            so_ids = so_obj.search(cr, uid, [('name', '=', data.get('origin'))]) or []
            for so in so_obj.browse(cr, uid, so_ids):
                data.update({'pts_id':so.pts_id and so.pts_id.id or False, 'dts_id':so.pts_id and so.pts_id.dts_id and so.pts_id.dts_id.id or False})
        
        return_type = data.get('return', 'none')
        sp = super(stock_picking, self).create(cr, uid, data, context=context)
        if data.get('type', 'internal') in ['in','out'] and data.get('pts_id', False) and return_type not in ['customer', 'supplier']:
            self.pool.get('delivery.route.line').create(cr, uid, {'picking_id':sp, })
        return sp

stock_picking()


class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'batch_id': fields.many2one('picking.batch', 'Picking Batch', change_default=True),
        'route_line_id': fields.one2many('delivery.route.line', 'picking_id', 'Delivery Time'),
        'so_payment_method': fields.char('Payment Method', size=32),
    }
        
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        pts_id = False
        if type(ids) != type([]):
            ids = [ids]
        if 'dts_id' in vals:
            move_pool = self.pool.get('stock.move')
            proc_pool = self.pool.get('procurement.order')
            pts_pool = self.pool.get('delivery.time')
            drl_pool = self.pool.get('delivery.route.line')
            
            if 'pts_id' not in vals:
                pts_id = pts_pool.search(cr, uid, [('active', '=', True), ('type', '=', 'pts'), ('dts_id', '=', vals['dts_id'])], order='start_date DESC')
                if pts_id:
                    pts_id = pts_id[0]
                    vals.update({'pts_id':pts_id})
            else:
                pts_id = vals['pts_id']
            
            if pts_id:
                move_ids = move_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('picking_id', 'in', ids)])
                if move_ids:
                    move_pool.write(cr, uid, move_ids, {'pts_id':pts_id})
                    proc_ids = proc_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('move_id', 'in', move_ids)])
                    if proc_ids:
                        proc_pool.write(cr, uid, proc_ids, {'pts_id':pts_id})
            
#            Actually DONE in fields.function
#            route_lines = drl_pool.search(cr, uid, [('state', 'in', ['draft']), ('picking_id', 'in', ids)])
#            if route_lines:
#                drl_pool.write(cr, uid, route_lines, {'dts_id': vals['dts_id']})
        return super(stock_picking_out, self).write(cr, uid, ids, vals, context=context)
    
    
    def pts_id_change(self, cr, uid, ids, pts_id, context=None):
        res = {}
        context = context or {}
        if type(ids) != type([]):
            ids = [ids]
        move_pool = self.pool.get('stock.move')
        proc_pool = self.pool.get('procurement.order')
        pts_pool = self.pool.get('delivery.time')
        drl_pool = self.pool.get('delivery.route.line')
        
        if pts_id:
            pts = pts_pool.browse(cr, uid, [pts_id])[0]
            #self.write(cr, uid, ids, {'dts_id':pts and pts.dts_id and pts.dts_id.id or False})
            res['dts_id'] = pts and pts.dts_id and pts.dts_id.id or False
        
        move_ids = move_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('picking_id', 'in', ids)])
        if move_ids:
            vals = {'pts_id':pts_id}
            if pts_id:
                vals.update({'date_expected':pts.dts_id.start_date})
            move_pool.write(cr, uid, move_ids, vals)
            proc_ids = proc_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('move_id', 'in', move_ids)])
            if proc_ids:
                proc_pool.write(cr, uid, proc_ids, {'pts_id':pts_id})
        
#        Actually DONE in fields.function
#        route_lines = drl_pool.search(cr, uid, [('state', 'in', ['draft']), ('picking_id', 'in', ids)])
#        if route_lines and 'dts_id' in res:
#            drl_pool.write(cr, uid, route_lines, {'dts_id': res['dts_id']})
        return {'value': res}
    

    def create(self, cr, uid, data, context=None):
        """
        create route line 
        """
        if not data.get('pts_id', False) and data.get('origin', False):
            so_obj = self.pool.get('sale.order')
            so_ids = so_obj.search(cr, uid, [('name', '=', data.get('origin'))]) or []
            for so in so_obj.browse(cr, uid, so_ids):
                data.update({'pts_id':so.pts_id and so.pts_id.id or False, 'dts_id':so.pts_id and so.pts_id.dts_id and so.pts_id.dts_id.id or False})
        
        return_type = data.get('return', 'none')
        sp = super(stock_picking_out, self).create(cr, uid, data, context=context)
        if data.get('pts_id', False) and return_type not in ['customer', 'supplier']:
            self.pool.get('delivery.route.line').create(cr, uid, {'picking_id':sp, })
        return sp

stock_picking_out()


class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
    _columns = {
        'batch_id': fields.many2one('picking.batch', 'Picking Batch', change_default=True),
        'route_line_id': fields.one2many('delivery.route.line', 'picking_id', 'Delivery Time'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        pts_id = False
        if type(ids) != type([]):
            ids = [ids]
        if 'dts_id' in vals:
            move_pool = self.pool.get('stock.move')
            proc_pool = self.pool.get('procurement.order')
            pts_pool = self.pool.get('delivery.time')
            drl_pool = self.pool.get('delivery.route.line')
            
            if 'pts_id' not in vals:
                pts_id = pts_pool.search(cr, uid, [('active', '=', True), ('type', '=', 'pts'), ('dts_id', '=', vals['dts_id'])], order='start_date DESC')
                if pts_id:
                    pts_id = pts_id[0]
                    vals.update({'pts_id':pts_id})
            else:
                pts_id = vals['pts_id']
            
            if pts_id:
                move_ids = move_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('picking_id', 'in', ids)])
                if move_ids:
                    move_pool.write(cr, uid, move_ids, {'pts_id':pts_id})
                    proc_ids = proc_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('move_id', 'in', move_ids)])
                    if proc_ids:
                        proc_pool.write(cr, uid, proc_ids, {'pts_id':pts_id})
                        
#            Actually DONE in fields.function
#            route_lines = drl_pool.search(cr, uid, [('state', 'in', ['draft']), ('picking_id', 'in', ids)])
#            if route_lines:
#                drl_pool.write(cr, uid, route_lines, {'dts_id': vals['dts_id']})
        return super(stock_picking_in, self).write(cr, uid, ids, vals, context=context)
    
    
    def pts_id_change(self, cr, uid, ids, pts_id, context=None):
        res = {}
        context = context or {}
        if type(ids) != type([]):
            ids = [ids]
        move_pool = self.pool.get('stock.move')
        proc_pool = self.pool.get('procurement.order')
        pts_pool = self.pool.get('delivery.time')
        drl_pool = self.pool.get('delivery.route.line')
        
        if pts_id:
            pts = pts_pool.browse(cr, uid, [pts_id])[0]
            #self.write(cr, uid, ids, {'dts_id':pts and pts.dts_id and pts.dts_id.id or False})
            res['dts_id'] = pts and pts.dts_id and pts.dts_id.id or False
        
        move_ids = move_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('picking_id', 'in', ids)])
        if move_ids:
            vals = {'pts_id':pts_id}
            if pts_id:
                vals.update({'date_expected':pts.dts_id.start_date})
            move_pool.write(cr, uid, move_ids, vals)
            proc_ids = proc_pool.search(cr, uid, [('state', 'not in', ['cancel', 'done']), ('move_id', 'in', move_ids)])
            if proc_ids:
                proc_pool.write(cr, uid, proc_ids, {'pts_id':pts_id})
        
#        Actually DONE in fields.function
#        route_lines = drl_pool.search(cr, uid, [('state', 'in', ['draft']), ('picking_id', 'in', ids)])
#        if route_lines and 'dts_id' in res:
#            drl_pool.write(cr, uid, route_lines, {'dts_id': res['dts_id']})
        return {'value': res}
    

    def create(self, cr, uid, data, context=None):
        """
        create route line 
        """
        if not data.get('pts_id', False) and data.get('origin', False):
            so_obj = self.pool.get('sale.order')
            so_ids = so_obj.search(cr, uid, [('name', '=', data.get('origin'))]) or []
            for so in so_obj.browse(cr, uid, so_ids):
                data.update({'pts_id':so.pts_id and so.pts_id.id or False, 'dts_id':so.pts_id and so.pts_id.dts_id and so.pts_id.dts_id.id or False})
        
        purchase_id = data.get('purchase_id', False)
        return_type = data.get('return', 'none')
        if purchase_id:
            po = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
            if not po.is_collected:
                purchase_id = False
        
        sp = super(stock_picking_in, self).create(cr, uid, data, context=context)
        if data.get('pts_id', False) and return_type not in ['customer', 'supplier'] and not purchase_id:
            self.pool.get('delivery.route.line').create(cr, uid, {'picking_id':sp, })
        return sp

stock_picking_in()


class stock_tracking(osv.osv):
    _inherit = "stock.tracking"
    
    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Picking Related', change_default=True),
        'ul_id': fields.many2one('product.ul', 'Picking Box', change_default=True),
    }
stock_tracking()


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'pts_id':  fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts')]),
    }
    
    def _make_production_internal_shipment_line(self, cr, uid, production_line, shipment_id, parent_move_id, destination_location_id=False, context=None):
        stock_move = self.pool.get('stock.move')
        production = production_line.production_id
        date_planned = production.date_planned
        # Internal shipment is created for Stockable and Consumer Products
        if production_line.product_id.type not in ('product', 'consu'):
            return False
        source_location_id = production.location_src_id.id
        if not destination_location_id:
            destination_location_id = source_location_id
        return stock_move.create(cr, uid, {
                        'name': production.name,
                        'picking_id': shipment_id,
                        'product_id': production_line.product_id.id,
                        'product_qty': production_line.product_qty,
                        'product_uom': production_line.product_uom.id,
                        'product_uos_qty': production_line.product_uos and production_line.product_uos_qty or False,
                        'product_uos': production_line.product_uos and production_line.product_uos.id or False,
                        'date': date_planned,
                        'move_dest_id': parent_move_id,
                        'location_id': source_location_id,
                        'location_dest_id': destination_location_id,
                        'state': 'waiting',
                        'company_id': production.company_id.id,
                        'pts_id': production.pts_id and production.pts_id.id or False,
                })
    
    def _make_production_internal_shipment(self, cr, uid, production, context=None):
        ir_sequence = self.pool.get('ir.sequence')
        stock_picking = self.pool.get('stock.picking')
        routing_loc = None
        pick_type = 'internal'
        partner_id = False

        # Take routing address as a Shipment Address.
        # If usage of routing location is a internal, make outgoing shipment otherwise internal shipment
        if production.bom_id.routing_id and production.bom_id.routing_id.location_id:
            routing_loc = production.bom_id.routing_id.location_id
            if routing_loc.usage != 'internal':
                pick_type = 'out'
            partner_id = routing_loc.partner_id and routing_loc.partner_id.id or False

        # Take next Sequence number of shipment base on type
        # SHOULD USE ir_sequence.next_by_code() or ir_sequence.next_by_id()
        pick_name = ir_sequence.get(cr, uid, 'stock.picking.' + pick_type)

        picking_id = stock_picking.create(cr, uid, {
            'name': pick_name,
            'origin': (production.origin or '').split(':')[0] + ':' + production.name,
            'type': pick_type,
            'move_type': 'one',
            'state': 'auto',
            'partner_id': partner_id,
            'auto_picking': self._get_auto_picking(cr, uid, production),
            'company_id': production.company_id.id,
            'pts_id': production.pts_id and production.pts_id.id or False,
            'dts_id': production.pts_id and production.pts_id.dts_id and production.pts_id.dts_id.id or False,
        })
        production.write({'picking_id': picking_id}, context=context)
        return picking_id

    def _make_production_produce_line(self, cr, uid, production, context=None):
        stock_move = self.pool.get('stock.move')
        source_location_id = production.product_id.property_stock_production.id
        destination_location_id = production.location_dest_id.id
        data = {
            'name': production.name,
            'date': production.date_planned,
            'product_id': production.product_id.id,
            'product_qty': production.product_qty,
            'product_uom': production.product_uom.id,
            'product_uos_qty': production.product_uos and production.product_uos_qty or False,
            'product_uos': production.product_uos and production.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': production.move_prod_id.id,
            'state': 'waiting',
            'company_id': production.company_id.id,
            'pts_id': production.pts_id and production.pts_id.id or False,
        }
        move_id = stock_move.create(cr, uid, data, context=context)
        production.write({'move_created_ids': [(6, 0, [move_id])]}, context=context)
        return move_id

    def _make_production_consume_line(self, cr, uid, production_line, parent_move_id, source_location_id=False, context=None):
        stock_move = self.pool.get('stock.move')
        production = production_line.production_id
        # Internal shipment is created for Stockable and Consumer Products
        if production_line.product_id.type not in ('product', 'consu'):
            return False
        destination_location_id = production.product_id.property_stock_production.id
        if not source_location_id:
            source_location_id = production.location_src_id.id
        move_id = stock_move.create(cr, uid, {
            'name': production.name,
            'date': production.date_planned,
            'product_id': production_line.product_id.id,
            'product_qty': production_line.product_qty,
            'product_uom': production_line.product_uom.id,
            'product_uos_qty': production_line.product_uos and production_line.product_uos_qty or False,
            'product_uos': production_line.product_uos and production_line.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': parent_move_id,
            'state': 'waiting',
            'company_id': production.company_id.id,
            'pts_id': production.pts_id and production.pts_id.id or False,
        })
        production.write({'move_lines': [(4, move_id)]}, context=context)
        return move_id
    
mrp_production()


class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    _columns = {
        'pts_id':  fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts')]),
        'message': fields.char(_('Latest error'), size=2048, help="Exception occurred while computing procurement orders."),
    }

    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
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
                'pts_id': procurement.pts_id and procurement.pts_id.id or context and context.get('force_pts_id', False) or False,
            })
            
            res[procurement.id] = produce_id
            self.write(cr, uid, [procurement.id], {'state': 'running', 'production_id': produce_id})   
            bom_result = production_obj.action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
            if res_id:
                move_obj.write(cr, uid, [res_id], {'location_id': procurement.location_id.id})
        self.production_order_create_note(cr, uid, ids, context=context)
        return res

procurement_order()


class delivery_time(osv.osv):
    _inherit = 'delivery.time'
    
    def search(self, cr, uid, args, offset=0, limit=None, order='name', context=None, count=False):
        # now = datetime.now()
        # args.append(('name','>=',datetime.strftime(now,'%y%m%d')))
        return super(delivery_time, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

delivery_time()


class delivery_return_type(osv.osv):
    _name = 'delivery.return.type'
    
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
        'sequence': fields.integer('Sequence'),
    }
    _order = 'sequence'
delivery_return_type()
    

class delivery_return_reason(osv.osv):
    _name = 'delivery.return.reason'
    
    _columns = {
        'type': fields.many2one('delivery.return.type', 'Type', required=True),
        'reason': fields.char('Name', size=1024, required=False),
        'route_line_id': fields.many2one('delivery.route.line', 'Delivery Route Line'),
    }
delivery_return_reason()


class delivery_route(osv.osv):
    _inherit = 'delivery.route'
    
    def _auto_init(self, cr, context=None):
        super(delivery_route, self)._auto_init(cr, context=context)
        cr.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'delivery_scheduler_running'")
        if not cr.fetchone():
            cr.execute('CREATE TABLE delivery_scheduler_running (running boolean)')
            cr.commit()
            cr.execute('INSERT INTO delivery_scheduler_running (running) VALUES (FALSE)')
    
    def set_confirm_cs(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'confirm_cs': True}, context=context)
        return True
    
delivery_route()

    
class delivery_route_line(osv.osv):
    _inherit = 'delivery.route.line'
    
    def search(self, cr, uid, args, offset=0, limit=None, order='dts_name', context=None, count=False):
        context = context or {}
        new_order = context.get('sorting', order)
        return super(delivery_route_line, self).search(cr, uid, args, offset=offset, limit=limit, order=new_order, context=context, count=count)
    
    def set_not_vip(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'vip':False})

    def set_vip(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'vip':True})
    
    def write(self, cr, uid, ids, vals, context=None):
        if type(ids) != type([]):
            ids = [ids]
        context = context or {}
        if ('route_id' in vals or 'color' in vals or 'sequence' in vals) and not 'force_update' in context:
            for line in self.browse(cr, uid, ids):
                if line.state == 'draft':
                    current_dts = context.get('force_dts_id_kanban', False) or False
                    # if current_dts:
                    #    vals.update({'dts_id':current_dts})
                    if 'route_id' in vals and vals['route_id']:
                        route_state = self.pool.get('delivery.route').read(cr, uid, [vals['route_id']], ['state', 'name'])
                        if route_state[0]['state'] != 'draft': 
                            print('The Route %s is confirmed, you can not add lines to it.' % (route_state[0]['name']))
                            raise osv.except_osv(_('Error'), _('The Route %s is confirmed, you can not add lines to it.' % (route_state[0]['name'])))
                        
                        elif 'update_color' in context and context['update_color'] == 1:
                            current_color = str(line.color)
                            cr.execute("SELECT color FROM (select count(*) as cpt, color as color from delivery_route_line WHERE route_id=" + str(vals['route_id']) + " AND color != " + current_color + " AND color IS NOT null AND color > 0 GROUP BY color) t ORDER BY cpt DESC")
                            color = cr.fetchone()
                            if color and color[0]:
                                vals.update({'color':color[0]})
                            
                            elif current_dts:
                                cr.execute("SELECT DISTINCT color FROM delivery_route_line WHERE (dts_id=" + str(current_dts) + " OR id = " + str(line.id) + ") AND color IS NOT null AND color > 0")
                                colors = map(lambda x: x[0], cr.fetchall())
                                color = False
                                
                                for idx in range(1, 22):
                                    if idx not in colors and not color and idx != current_color:
                                        color = idx
                                if color:
                                    vals.update({'color':color})
                                else:
                                    print('No more Route available for the DTS %s.' % (line.dts_id.name))
                                    raise osv.except_osv(_('Error'), _('No more Route available for the DTS %s.' % (line.dts_id.name)))
                    
                    elif 'check4color' in context and context['check4color'] and 'color' in vals:
                        cr.execute("SELECT DISTINCT route_id FROM delivery_route_line WHERE dts_id=" + str(line.dts_id.id) + " AND color = " + str(vals['color']) + " AND color > 0 AND state not in ('draft','cancel')")
                        route_line_ids = map(lambda x: x[0], cr.fetchall())
                        if route_line_ids:
                            print('The Route Line %s (origin: %s) can not be put in a confirmed Route (%s).' % (line.picking_id.name, line.picking_id.origin, route_line_ids))
                            raise osv.except_osv(_('Error'), _('The Route Line %s (origin: %s) can not be put in a confirmed Route (%s).' % (line.picking_id.name, line.picking_id.origin, route_line_ids)))
                else:
                    print('The Route Line %s (origin: %s) is confirmed. You can not change it.' % (line.picking_id.name, line.picking_id.origin))
                    raise osv.except_osv(_('Error'), _('The Route Line %s (origin: %s) is confirmed. You can not change it.' % (line.picking_id.name, line.picking_id.origin)))
        return super(delivery_route_line, self).write(cr, uid, ids, vals, context=context)
    
    
    def set_van(self, cr, uid, ids, van=0, context=None):
        self.write(cr, uid, ids, {'color': van}, context=context)
        return True
    def set_van_0(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 0, context)
    def set_van_1(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 1, context)
    def set_van_2(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 2, context)
    def set_van_3(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 3, context)
    def set_van_4(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 4, context)
    def set_van_5(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 5, context)
    def set_van_6(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 6, context)
    def set_van_7(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 7, context)
    def set_van_8(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 8, context)
    def set_van_9(self, cr, uid, ids, context=None):
        return self.set_van(cr, uid, ids, 9, context)
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        context = context or {}
        if 'view_name' in context and view_type == 'kanban':
            view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'delivery.route.line'), ('name', '=', context['view_name'])], context=context)
            if view_ids:
                view_id = view_ids[0]
                del context['view_name']
        return super(delivery_route_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    
    
    def _get_neighborhood(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for route in self.browse(cr, uid, ids):
            # res[route.id] = route.picking_id and route.picking_id.sale_id and route.picking_id.sale_id.deliver_zone or route.picking_id and route.picking_id.partner_id and route.picking_id.partner_id.vm_district or False
            res[route.id] = route.picking_id and route.picking_id.partner_id and route.picking_id.partner_id.deliver_zone or False
        return res
    
    def _get_dts_id(self, cr, uid, ids, fields, args, context=None):
        context = context or {}
        res = {}
        for route in self.browse(cr, uid, ids):
            if route.state in ['draft'] and context.get('set_dts', True):
                res[route.id] = route.picking_id and route.picking_id.pts_id and route.picking_id.pts_id.dts_id and route.picking_id.pts_id.dts_id.id or False
            else:
                res[route.id] = route.dts_id and route.dts_id.id or False
        return res
    
    def _get_dts_name(self, cr, uid, ids, fields, args, context=None):
        context = context or {}
        res = {}
        for route in self.browse(cr, uid, ids):
            if route.state in ['draft'] and context.get('set_dts', True):
                res[route.id] = route.picking_id and route.picking_id.pts_id and route.picking_id.pts_id.dts_id and route.picking_id.pts_id.dts_id.name or 'n/a'
            else:
                res[route.id] = route.dts_name or 'n/a'
        return res
    
    def _get_special_time(self, cr, uid, ids, fields, args, context=None):
        tz = pytz.timezone('Asia/Shanghai')
        result = {}
        for route in self.browse(cr, uid, ids):
            res = {}
            customer_date = ''
            route_dts_id = route.dts_id and route.dts_id.id
            so_dts_id    = route.picking_id.sale_id.dts_id and route.picking_id.sale_id.dts_id.id
            
            if so_dts_id and route_dts_id != so_dts_id:
                customer_date = route.picking_id.sale_id.dts_id.name
            
            elif route.picking_id.sale_id:
                date_start = route.picking_id.sale_id.start_date or False
                date_end = route.picking_id.sale_id.end_date or False
                
                if date_start:
                    date_start = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')            
                    date_start = pytz.utc.localize(date_start).astimezone(tz)
                    
                    customer_date = datetime.strftime(date_start, '%H:%M')
                    #LY if customer_date is 00:00, no special time. 
                    if customer_date != '00:00':    
                        if date_end:
                            date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')            
                            date_end = pytz.utc.localize(date_end).astimezone(tz)
                            customer_date += ' - '
                            customer_date += datetime.strftime(date_end, '%H:%M')
            res['customer_date'] = customer_date or ' '
            result[route.id] = res
        return result
    
    def _get_street(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for route in self.browse(cr, uid, ids):
            res[route.id] = route.picking_id and route.picking_id.partner_id and route.picking_id.partner_id.street or ' n/a'
        return res
    
    def _route_to_update_after_picking_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('delivery.route.line').search(cr, uid, [('picking_id', 'in', ids)]) or []
    
    def _route_to_update_after_dts_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        picking_ids = self.pool.get('stock.picking').search(cr, uid, [('dts_id', 'in', ids)]) or []
        return self.pool.get('delivery.route.line')._route_to_update_after_picking_change(cr, uid, picking_ids, None, None, context=context)
    
    def _route_to_update_after_so_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('delivery.route.line').search(cr, uid, [('sale_order_id', 'in', ids)]) or []
    
    def _route_to_update_after_po_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('delivery.route.line').search(cr, uid, [('purchase_id', 'in', ids)]) or []
    
    def _route_to_update_after_partner_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        picking_ids = self.pool.get('stock.picking').search(cr, uid, [('partner_id', 'in', ids)]) or []
        return self.pool.get('delivery.route.line')._route_to_update_after_picking_change(cr, uid, picking_ids, None, None, context=context)
    
    _store_dts = {
        'delivery.route.line': (lambda self, cr, uid, ids, context: ids, ['picking_id'], 10),
        'stock.picking': (_route_to_update_after_picking_change, ['pts_id'], 10),
    }
    _store_dts_name = {
        'delivery.route.line': (lambda self, cr, uid, ids, context: ids, ['picking_id'], 10),
        'stock.picking': (_route_to_update_after_picking_change, ['pts_id'], 10),
        'delivery.time': (_route_to_update_after_dts_change, ['name'], 10),
    }
    _store_special_time = {
        'delivery.route.line': (lambda self, cr, uid, ids, context: ids, ['picking_id'], 12),
        'stock.picking': (_route_to_update_after_picking_change, ['sale_id','dts_id'], 12),
        'sale.order': (_route_to_update_after_so_change, ['dts_id'], 12),
    }
    _store_neighborhood = {
        'delivery.route.line': (lambda self, cr, uid, ids, context: ids, ['picking_id'], 10),
        'stock.picking': (_route_to_update_after_picking_change, ['partner_id'], 10),
        'res.partner': (_route_to_update_after_partner_change, ['vm_district'], 10),
    }
    
    _store_amount = {
        'delivery.route.line': (lambda self, cr, uid, ids, context: ids, ['picking_id', 'adjustment'], 10),
        'stock.picking': (_route_to_update_after_picking_change, ['sale_id', 'purchase_id', 'origin'], 10),
        'purchase.order': (_route_to_update_after_po_change, ['amount_total'], 10),
    }
    
    _store_street = {
        'delivery.route.line': (lambda self,cr,uid,ids,context: ids,['picking_id'],10), 
        'stock.picking': (_route_to_update_after_picking_change, ['partner_id'], 10),
    }
    
    def _get_amount(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for route in self.browse(cr, uid, ids):
            res = {}
            res['amount_total'] = 0.0
            res['amount_unpaid'] = 0.0
            res['to_be_received'] = 0.0
            
            if route.picking_id and route.picking_id.sale_id:
                res['amount_total'] = route.picking_id.sale_id.amount_total
                res['amount_unpaid'] = res['amount_total']
                res['to_be_received'] = res['amount_unpaid'] + route.adjustment
            elif route.picking_id and route.picking_id.purchase_id:
                res['amount_total'] = route.picking_id.purchase_id.amount_total
                res['amount_unpaid'] = 0.0
                res['to_be_received'] = res['amount_unpaid'] + route.adjustment
            result[route.id] = res
        return result
    
    _columns = {
        'dts_id': fields.function(_get_dts_id, type='many2one', obj='delivery.time', store=_store_dts, string='Delivery Time', _classic_read=True),
        'dts_name': fields.function(_get_dts_name, type='char', size=124, store=_store_dts_name, string='Delivery Time'),
        'return_reasons': fields.one2many('delivery.return.reason', 'route_line_id', 'Return Reasons', readonly=False),
        'delivered_cpt': fields.related('picking_id', 'delivered_cpt', type='integer', string='Delivered x times', readonly=True),
        'customer_date': fields.function(_get_special_time, type='char', size=64, store=_store_special_time, multi="special_time", string=_('Customer Delivery Time')),
        'neighborhood': fields.function(_get_neighborhood, type='char', size=255, store=_store_neighborhood, string=_('Neighborhood')),
        'street': fields.function(_get_street, type='char', size=128, store=_store_street, string='Street'),
        'vip': fields.boolean('is VIP ?'),
        'amount_total':  fields.function(_get_amount, type='float', multi="amount", store=_store_amount, string='Total'),
        'amount_unpaid': fields.function(_get_amount, type='float', multi="amount", store=_store_amount, string='Unpaid'),
        'adjustment': fields.float('Adjustment'),
        'cs_remark': fields.text('CS Remark'),
        'to_be_received': fields.function(_get_amount, type='float', multi="amount", store=_store_amount, string='To be Received'),
        'amount_received': fields.float('Received'),
        'account_checked': fields.boolean('Checked'),
        'account_remark': fields.text('Remark Accounting'),
    }
delivery_route_line()


class res_users(osv.osv):
    _inherit = 'res.users'
    
    _columns = {
        'dts_id': fields.many2one('delivery.time', 'Last Used Delivery Time'),
    }
res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
