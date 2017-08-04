# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import os
import psutil
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class stock_fill_inventory(osv.TransientModel):
    _inherit = "stock.fill.inventory"

    def fill_inventory(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventory_line_obj = self.pool.get('stock.inventory.line')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        if ids and len(ids):
            ids = ids[0]
        else:
             return {'type': 'ir.actions.act_window_close'}
        fill_inventory = self.browse(cr, uid, ids, context=context)
        res = {}
        res_location = {}
        
        self.pid = os.getpid()
        rss, vms = psutil.Process(os.getpid()).get_memory_info()
        _logger.debug('>>>>>>>>>> 1.  Worker (%d) virtual memory reached %s.'%(self.pid, vms))

        if fill_inventory.recursive:
            location_ids = location_obj.search(cr, uid, [('location_id',
                             'child_of', [fill_inventory.location_id.id])], order="id",
                             context=context)
        else:
            location_ids = [fill_inventory.location_id.id]

        res = {}
        flag = False

        for location in location_ids:
            datas = {}
            res[location] = {}
            move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done')], context=context)
            
            LIMIT = 10000
            for i in range(0,len(move_ids),LIMIT):
                #print datetime.now()
                move_ids_limit = move_ids[i:i+LIMIT]
                #print ">>>>>>start: %s, len move_ids %d, len datas: %d"%(i,len(move_ids_limit),len(datas))
                _logger.debug('>>>>>>>>>> 1.  Worker (%d) virtual memory reached %s.'%(self.pid, vms))
                rss, vms = psutil.Process(os.getpid()).get_memory_info()
                #print '>>>>>>>>>> 2.  Worker (%d) virtual memory reached %s.'%(self.pid, vms)
                _logger.debug('>>>>>>>>>> 2.  Worker (%d) virtual memory reached %s.'%(self.pid, vms))
                for move in move_obj.browse(cr, uid, move_ids_limit, context=context):
                    lot_id = move.prodlot_id.id
                    prod_id = move.product_id.id
                    if move.location_dest_id.id != move.location_id.id:
                        if move.location_dest_id.id == location:
                            qty = uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
                        else:
                            qty = -uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
     
     
                        if datas.get((prod_id, lot_id)):
                            qty += datas[(prod_id, lot_id)]['product_qty']
     
                        datas[(prod_id, lot_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': qty, 'product_uom': move.product_id.uom_id.id, 'prod_lot_id': lot_id}
     
            if datas:
                flag = True
                res[location] = datas
            
            print ">>>>>>>>>>%s"%datas
            rss, vms = psutil.Process(os.getpid()).get_memory_info()
            _logger.debug('>>>>>>>>>> 3.  Worker (%d) virtual memory reached %s.'%(self.pid, vms))
             
            if not flag:
                raise osv.except_osv(_('Warning!'), _('No product in this location. Please select a location in the product form.'))
     
            for stock_move in res.values():
                for stock_move_details in stock_move.values():
                    stock_move_details.update({'inventory_id': context['active_ids'][0]})
                    domain = []
                    for field, value in stock_move_details.items():
                        if field == 'product_qty' and fill_inventory.set_stock_zero:
                            domain.append((field, 'in', [value,'0']))
                            continue
                        domain.append((field, '=', value))
     
                    if fill_inventory.set_stock_zero:
                        stock_move_details.update({'product_qty': 0})
     
                    line_ids = inventory_line_obj.search(cr, uid, domain, context=context)
     
                    if not line_ids:
                        inventory_line_obj.create(cr, uid, stock_move_details, context=context)
            rss, vms = psutil.Process(os.getpid()).get_memory_info()
            _logger.debug('>>>>>>>>>> 4.  Worker (%d) virtual memory reached %s.'%(self.pid, vms))

        return {'type': 'ir.actions.act_window_close'}

stock_fill_inventory()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
