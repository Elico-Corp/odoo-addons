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

from osv import fields, osv
import netsvc
from tools.translate import _

class stock_batch_track(osv.osv_memory):
    _name = "stock.batch.track"
    _description = "Stock Batch Track"

    _columns = {
        'tracking_id': fields.many2one('stock.tracking', 'Pack', ),
        'partner_id': fields.many2one('res.partner', 'Subcontractor', ),
        'cancel_availability': fields.boolean('Cancel availability if availble?'),
        'check_availability': fields.boolean('Check availability if not availble?'),
        'force_availability': fields.boolean('Force availability if not availble?'),
        'auto_process': fields.boolean('Auto Proccess if availble?'),
    }
    _defaults = {
        'auto_process': True,
    }

    def process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sbt_data = self.read(cr, uid, ids, ['tracking_id', 'partner_id', 'cancel_availability', 'check_availability', 'force_availability', 'auto_process'])[0]

        wf_service = netsvc.LocalService("workflow")
        active_ids = context.get('active_ids', [])
        picking_pool = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        active_pickings = picking_pool.browse(cr, uid, active_ids, context=context)
        if not active_pickings:
            raise osv.except_osv(_('Warning !'),_('Please select pickings at first.'))

        for picking in active_pickings:
            if picking.state in ('cancel'):
                active_ids.remove(picking.id)
        
        active_pickings = picking_pool.browse(cr, uid, active_ids, context=context)
        todo_ids = []
        if sbt_data['tracking_id']:
            for picking in active_pickings:
                for move in picking.move_lines:
                    if move.state in ('cancel') or move.tracking_id:
                        continue
                    todo_ids.append(move.id)
            if todo_ids:
                move_obj.write(cr, uid, todo_ids, {'tracking_id': sbt_data['tracking_id']})
                if sbt_data['partner_id']:
                    self.pool.get('stock.tracking').write(cr, uid, sbt_data['tracking_id'], {'partner_id': sbt_data['partner_id']})
                active_pickings = picking_pool.browse(cr, uid, active_ids, context=context)
        
        if sbt_data['cancel_availability']:
            for picking in active_pickings:
                if picking.state in ('done','cancel','auto','confirmed'):
                    continue
                if picking.state in ('','assigned'):
                    picking_pool.cancel_assign(cr, uid, [picking.id], context)
            active_pickings = picking_pool.browse(cr, uid, active_ids, context=context)

        if sbt_data['check_availability']:
            for picking in active_pickings:
                if picking.state in ('assigned','done','cancel'):
                    continue
                if picking.state in ('auto'):
                    picking_pool.action_confirm(cr, uid, [picking.id], context)
                if picking.state in ('confirmed'):
                    picking_pool.action_assign(cr, uid, [picking.id], context)
            active_pickings = picking_pool.browse(cr, uid, active_ids, context=context)

        if sbt_data['force_availability']:
            for picking in active_pickings:
                if picking.state in ('confirmed'):
                    picking_pool.force_assign(cr, uid, [picking.id], context)
                                
        if sbt_data['auto_process']:
            for picking in active_pickings:
                if picking.state in ('assigned'):
                    wf_service.trg_validate(uid, 'stock.picking', picking.id, 'button_done', cr)

        action = {}
        pick_type = 'out'
        if active_ids:
            pick_type = picking_pool.read(cr, uid, [active_ids[0]], ['type'])[0]['type']
        if sbt_data['tracking_id']:
            action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_tracking_form')
        elif pick_type == 'in':
            action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
        elif pick_type == 'out':
            action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_picking_tree')
        else:
            action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_picking_tree6')

        action_pool = self.pool.get(action_model)
        action = action_pool.read(cr, uid, action_id, context=context)
        if sbt_data['tracking_id']:
            action['domain'] = "[('id','=', " + str(sbt_data['tracking_id']) +" )]"
        else:
            action['domain'] = "[('id','in', ["+','.join(map(str, active_ids))+"])]"
        return action

stock_batch_track()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
