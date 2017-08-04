# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import fields, osv
import netsvc
from openerp.tools.translate import _
import pooler

class stock_batch_move(osv.osv_memory):
    _name = "stock.batch.move"
    _description = "Stock Batch Move"

    _columns = {
        'cancel_availability': fields.boolean('Cancel availability if available?'),
        'check_availability': fields.boolean('Check availability if not available?'),
        'force_availability': fields.boolean('Force availability if not available?'),
        'auto_process': fields.boolean('Auto Process if available?'),
        'cancel_move': fields.boolean('Cancel the move?'),
    }
    _defaults = {
        'auto_process': True,
    }

    def process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sbt_data = self.read(cr, uid, ids, ['cancel_move', 'cancel_availability', 'check_availability', 'force_availability', 'auto_process'])[0]

        wf_service = netsvc.LocalService("workflow")
        active_ids = context.get('active_ids', [])
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        active_moves = move_obj.browse(cr, uid, active_ids, context=context)
        if not active_moves:
            raise osv.except_osv(_('Warning !'), _('Please select stock moves at first.'))

        for move in active_moves:
            if move.state in ('cancel'):
                active_ids.remove(move.id)
        
        active_moves = move_obj.browse(cr, uid, active_ids, context=context)
        
        if sbt_data['cancel_move']:
            todo_picking = []
            for move in active_moves:
                if move.state in ('done', 'cancel'):
                    continue
                move_obj.action_cancel(cr, uid, [move.id], context)                
                if move.picking_id and move.picking_id.id not in todo_picking:
                    todo_picking.append(move.picking_id.id)
            if todo_picking:
                for pick in pick_obj.browse(cr, uid, todo_picking, context=context):
                    if pick.state in ('cancel', 'done'):
                        continue
                                                
                    if pick.state in ('auto'):
                        wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_confirm', cr)

                    if pick.state in ('confirmed'):
                        try:
                            if pick_obj.test_assigned(cr, uid, [pick.id]):
                                if pick_obj.action_assign(cr, uid, [pick.id], None):
                                    pick_obj.action_assign_wkf(cr, uid, [pick.id], None)
                        except:
                            pass
                    # if pick.state in ('assigned'):
                    #    if pick_obj.test_finished(cr, uid, [pick.id]):
                    #        wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                            
                    # cancel = True
                    # for move in pick.move_lines:
                    #    if move.state not in ('cancel') and not move.scrapped:
                    #        cancel = False
                    #        break
                    if pick_obj.test_finished(cr, uid, [pick.id]):  # if cancel:
                        wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                        
            active_moves = move_obj.browse(cr, uid, active_ids, context=context)
        cr.commit()            
        if sbt_data['cancel_availability']:
            for move in active_moves:
                if move.state in ('done', 'cancel', 'auto', 'confirmed'):
                    continue
                if move.state in ('', 'assigned'):
                    move_obj.cancel_assign(cr, uid, [move.id], context)            
            active_moves = move_obj.browse(cr, uid, active_ids, context=context)
        cr.commit()
        if sbt_data['check_availability']:
            for move in active_moves:
                if move.state in ('assigned', 'done', 'cancel'):
                    continue
                if move.state in ('auto'):
                    move_obj.action_confirm(cr, uid, [move.id], context)
                if move.state in ('confirmed'):
                    move_obj.action_assign(cr, uid, [move.id], context)
            active_moves = move_obj.browse(cr, uid, active_ids, context=context)
        cr.commit()
        if sbt_data['force_availability']:
            for move in active_moves:
                if move.state in ('confirmed'):
                    move_obj.force_assign(cr, uid, [move.id], context)
        cr.commit() 
        #move_cr = pooler.get_db(cr.dbname).cursor()                               
        if sbt_data['auto_process']:
            for move in active_moves:
                if move.state in ('assigned'):
                    move_obj.action_done(cr, uid, [move.id], context)
                    cr.commit()
        #move_cr.close()

        action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_move_form2')

        action_pool = self.pool.get(action_model)
        action = action_pool.read(cr, uid, action_id, context=context)
        action['domain'] = "[('id','in', [" + ','.join(map(str, active_ids)) + "])]"
        return action

stock_batch_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
