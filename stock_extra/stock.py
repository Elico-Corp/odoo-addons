# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from osv import osv, fields
from openerp import tools
from tools.translate import _
import netsvc
import time
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

import openerp.addons.decimal_precision as dp


#LY 0514
class stock_return_reason(osv.osv):
    _name = 'stock.return.reason'
    _description = 'Stock Return Reason'
    _rec_name = "code"
    _order = 'code'
    
    _columns = {
        'code': fields.char('Code', size=12),
        'name': fields.char('Name', size=64),
        'active':fields.boolean('Active ?'),
    }
    _defaults = {
       'active':True,
    }
stock_return_reason()


class StockPicking(osv.osv):
    _inherit = 'stock.picking'
    _order = 'date desc'
    
    _columns = {
        'return': fields.selection([('none', 'Normal'), ('customer', 'Return from Customer'), ('supplier', 'Return to Supplier')], 'Type', required=True, select=True, help="Type specifies whether the Picking has been returned or not."),
        'write_date':  fields.datetime('Last Modification', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Updated by', readonly=True),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
    }
    _defaults = {    
        'return': 'none',
        'type':   'internal',
    }

StockPicking()


class StockPickingIn(osv.osv):
    _inherit = 'stock.picking.in'
    _order = 'date desc'
    
    def _partial_picking_change(self,cr,uid,ids,context=None):
        result = []
        for partial in self.browse(cr, uid, ids, context=context):
            result.append(partial.picking_id.id)
        result = list(set(result))
        return result
        
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    _columns = {    
        'return': fields.selection([('none', 'Normal'), ('customer', 'Return from Customer'), ('supplier', 'Return to Supplier')], 'Type', required=True, select=True, help="Type specifies whether the Picking has been returned or not."),
        'write_date':  fields.datetime('Last Modification', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Updated by', readonly=True),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
    }
    _defaults = {    
        'return': 'none',
        'type':   'in',
    }

StockPickingIn()


class StockPickingOut(osv.osv):
    _inherit = 'stock.picking.out'
    _order = 'date desc'

#    def search(self, cr, uid, args, offset=0, limit=None, order='name', context=None, count=False):
#        new_args = []
#        for arg in args:
#            if len(arg)==3 and arg[0]=='name':
#                new_args.append('|')
#                new_args.append(('origin',arg[1],arg[2]))
#            new_args.append(arg)
#        return super(StockPickingOut, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def _partial_picking_change(self,cr,uid,ids,context=None):
        result = []
        for partial in self.browse(cr, uid, ids, context=context):
            result.append(partial.picking_id.id)
        result = list(set(result))
        return result


    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    _columns = {    
        'return': fields.selection([('none', 'Normal'), ('customer', 'Return from Customer'), ('supplier', 'Return to Supplier')], 'Type', required=True, select=True, help="Type specifies whether the Picking has been returned or not."),
        'write_date':  fields.datetime('Last Modification', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Updated by', readonly=True),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
    }
    _defaults = {    
        'return': 'none',
        'type':   'out',
    }

StockPickingOut()


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    _name = "stock.partial.picking"

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking', 'stock.picking.in', 'stock.picking.out'), 'Bad context propagation'
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'move_ids' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
            if 'only_available' in context:
                moves = [self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state in ('assigned')]
            else:
                moves = [self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state not in ('done', 'cancel')]
            res.update(move_ids=moves)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res
    
stock_partial_picking()


class stock_return_picking(osv.osv):
    _inherit = 'stock.return.picking'

    def _get_return_type(self, cr, uid, context=None):
        if not context:
            context = {}
        
        type = context.get('default_type', False)
        if type == 'in':
            return 'supplier'
        elif type == 'out':
            return 'customer'
        return 'none'

    _columns = {
        'return_type': fields.selection([('none', 'Normal'), ('customer', 'Return from Customer'), ('supplier', 'Return to Supplier')], 'Type', required=True, select=True, help="Type specifies whether the Picking has been returned or not."),
        'note':        fields.text('Notes'),
        'location_id': fields.many2one('stock.location', 'Location', help='If a location is chosen the destination location for customer return (or origin for supplier return) is forced for all moves.'),
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
    }
    _defaults = {
        'return_type': lambda self, cr, uid, context: self._get_return_type(cr, uid, context=context),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick and pick.sale_id and pick.sale_id:
            warehouse = pick.sale_id.shop_id and pick.sale_id.shop_id.warehouse_id
            res.update({'location_id': warehouse and warehouse.lot_return_id and warehouse.lot_return_id.id or False})
        
        if pick:
            result1 = []
            return_history = self.get_return_history(cr, uid, record_id, context)       
            for line in pick.move_lines:
                if line.state in ('cancel') or line.scrapped:
                    continue
                qty = line.product_qty - return_history.get(line.id, 0)
                if qty > 0:
                    result1.append({'product_id': line.product_id.id, 'quantity': qty, 'move_id':line.id})
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})
        return res
    
    def create_returns(self, cr, uid, ids, context=None):
        """ 
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {} 
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.memory')
        act_obj = self.pool.get('ir.actions.act_window')
        model_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = False#True LY by default 
        returned_lines = 0
        return_type = 'customer'
        
        # Create new picking for returned products
        if pick.type == 'out':
            new_type = 'in'
        elif pick.type == 'in':
            new_type = 'out'
        else:
            new_type = 'internal'
        
        seq_obj_name = 'stock.picking.' + new_type
        # SHOULD USE ir_sequence.next_by_code() or ir_sequence.next_by_id()
        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        new_picking_vals = {'name': _('%s-%s-return') % (new_pick_name, pick.name),
                            'move_lines': [],
                            'state':'draft',
                            'type': new_type,
                            'return': data['return_type'],
                            'note': data['note'],
                            'return_reason_id': data['return_reason_id'] and data['return_reason_id'][0],#data return (id,code) eg. (10, 'operation')
                            'date':date_cur,
                            'invoice_state': data['invoice_state'], }
        new_picking = pick_obj.copy(cr, uid, pick.id, new_picking_vals)
        
        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            if move.state in ('cancel') or move.scrapped:
                continue
            new_location = move.location_dest_id.id
            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            #if  data['invoice_state'] == 'none':#returned_qty == new_qty #!= new_qty:
            #    set_invoice_state_to_none = True#LY False
            if new_qty:
                returned_lines += 1
                new_move_vals = {'product_qty': new_qty,
                                'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                'picking_id': new_picking,
                                'state': 'draft',
                                'location_id': new_location,
                                'location_dest_id': move.location_id.id,
                                'date': date_cur,
                                'note': data['note'],
                                'return_reason_id': data['return_reason_id'] and data['return_reason_id'][0], }#data return (id,code) eg. (10, 'operation')
                if data['location_id']:
                    if data['return_type'] == 'customer':
                        new_move_vals.update({'location_dest_id': data['location_id'][0], })
                    else:
                        new_move_vals.update({'location_id': data['location_id'][0], })
                
                new_move = move_obj.copy(cr, uid, move.id, new_move_vals)
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4, new_move)]}, context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        #LY make it can be invoiced
        if data['invoice_state'] == 'none':#returned_qty == new_qty #!= new_qty:
            set_invoice_state_to_none = True#LY False
        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        # Update view id in context, lp:702939
        model_list = {
                'out': 'stock.picking.out',
                'in': 'stock.picking.in',
                'internal': 'stock.picking',
        }
        return {
            'domain': "[('id', 'in', [" + str(new_picking) + "])]",
            'name': _('Returned Picking'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model': model_list.get(new_type, 'stock.picking'),
            'type':'ir.actions.act_window',
            'context':context,
        }

stock_return_picking()

class stock_move_scrap(osv.osv_memory):
    _inherit = "stock.move.scrap"
    _name = "stock.move.scrap"

    _columns = {
        'note': fields.text('Return reason'),
    }
    _defaults = {
        'location_id': lambda *x: False
    }

    
    def move_scrap(self, cr, uid, ids, context=None):
        """ To move scrapped products
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        move_ids = context['active_ids']
        for data in self.browse(cr, uid, ids):
            context.update({'note': data.note})
            move_obj.action_scrap(cr, uid, move_ids,
                             data.product_qty, data.location_id.id,
                             context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_move_scrap()


class StockMove(osv.osv):
    _inherit = 'stock.move'
    
#    def _auto_init(self,cr, context=None):
#        super(StockMove, self)._auto_init(cr, context=context)
#        cr.execute("""
#                SELECT m.id FROM stock_move m
#                left join stock_picking p on p.id = m.picking_id
#                WHERE p.type = 'in'
#                AND m.po_price IS NULL; 
#        """)
#        move_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
#        for move in self.browse(cr, 1, move_ids):
#            print "========= %s: %s ========"%(move.po_price, move.amount_total)
#            self.write(cr, 1, move.id, 
#                       {
#                       'po_price':move.po_price, # TO BE REMOVED AFTER THE po_price FIELDS 1ST CALCULATION
#                       'amount_total':move.amount_total,# TO BE REMOVED AFTER THE amount_total FIELDS 1ST CALCULATION
#                       })
#        return True


    def action_assign(self, cr, uid, ids, *args):
        #Overwritten to use .read() instead of .browse() which is slower
        """ Changes state to confirmed or waiting.
        @return: List of values
        """
        todo = []
        for move in self.read(cr, uid, ids, ['state']):
            if move['state'] in ('confirmed', 'waiting'):
                todo.append(move['id'])
            #LY concurrent udpate
            res = self.check_assign(cr, uid, todo)
            cr.commit()
            #END
        #LY 0515 res = self.check_assign(cr, uid, todo)
        return res
    
    
    def action_pop_mo(self, cr, uid, ids, context=None):
        mo_ids = False
        context = context or {}
        
        id = ids or context.get('active_ids', False) or False
        if id:
            id = id[0]

        domain = [('id', 'in', (-1,))]
        for move in self.browse(cr, uid, [id], context=context):
            if move.product_id and  move.pts_id:                    
                mo_ids = self.pool.get('mrp.production').search(cr, uid, [('pts_id', '=', move.pts_id.id), ('product_id', '=', move.product_id.id)])
                if mo_ids:
                    domain = [('id', 'in', tuple(mo_ids))]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _("Related Manufacturing Order"),
            'view_mode': 'tree,form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'mrp.production',
            'domain': domain,
            #'context': context
        }
    
    def _get_qty_available(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
           if move.product_id:
               result[move.id] = move.product_id.qty_available
           else:
               result[move.id] = 0
        return result
    
    
    def _get_product_code(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
            result[move.id] = move.product_id and move.product_id.default_code or 'No ref'
        return result
    
    
    def _get_stock_type(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
           if move.product_id and move.product_id.stock_type_id:
               result[move.id] = move.product_id.stock_type_id.name[:2]
           else:
               result[move.id] = 'None'
        return result
    
    def _move_to_update_folowing_type_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        product_ids = self.pool.get('product.product').search(cr, uid, [('stock_type_id', 'in', ids)]) or []
        return self.pool.get('stock.move').search(cr, uid, [('product_id', 'in', product_ids)]) or []
        
    def _move_to_update_folowing_product_type_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('stock.move').search(cr, uid, [('product_id', 'in', ids)]) or []
    
    _store_stock_type = {
        'stock.move': (lambda self, cr, uid, ids, context: ids, ['product_id'], 10),
        'product.stock_type': (_move_to_update_folowing_type_change, ['name'], 10),
        'product.product': (_move_to_update_folowing_product_type_change, ['stock_type_id'], 10)
    }
    
    def _get_product_supply_method(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
            type = '-'
            if move.product_id:
                if move.product_id.supply_method == 'buy':
                    type = 'B'
                elif move.product_id.supply_method == 'produce':
                    # if move.product_id.auto_mo:
                    type = 'A'
                    # else:
                    #     type = 'M'
                else:
                    type = 'O'
            result[move.id] = type
        return result
        
    def _move_to_update_after_product_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('stock.move').search(cr, uid, [('product_id', 'in', ids)]) or []
    
    _store_product_supply_method = {
        'stock.move': (lambda self, cr, uid, ids, context: ids, ['product_id'], 10),
        'product.product': (_move_to_update_after_product_change, ['supply_method', 'auto_mo'], 10),
    }
    _store_product_code = {
        'stock.move': (lambda self, cr, uid, ids, context: ids, ['product_id'], 10),
        'product.product': (_move_to_update_after_product_change, ['default_code'], 10),
    }
    
#    def _get_partner_ref(self, cr, uid, ids, fields, args, context=None):
#        result = {}
#        for move in self.browse(cr, uid, ids, context=context):
#            result[move.id] = move.partner_id and move.partner_id.ref or 'No ref'
#        return result
#    
#    def _move_to_update_folowing_partner_change(self, cr, uid, ids, fields=None, arg=None, context=None):
#        if type(ids) != type([]):
#            ids = [ids]
#        return self.pool.get('stock.move').search(cr, uid, [('partner_id', 'in', ids)]) or []
#    
#    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
#        res = {}
#        cur_obj = self.pool.get('res.currency')
#        tax_obj = self.pool.get('account.tax')
#        for line in self.browse(cr, uid, ids, context=context):
#            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.po_price, line.product_qty, line.product_id, line.picking_id.partner_id)
#            cur = line.purchase_line_id.order_id.pricelist_id.currency_id
#            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
#        return res
    
    _columns = {
        'product_supply_method': fields.function(_get_product_supply_method, method=True, type='char', size=32, string='Product Supply Method', store=_store_product_supply_method, readonly=True),
        'stock_type': fields.function(_get_stock_type, method=True, type='char', size=1024, store=_store_stock_type, string='T'),
        'qty_available': fields.function(_get_qty_available, method=True, type='float', digits=(12, 3), string='Quantity Available', readonly=True),
        'product_code':  fields.function(_get_product_code, method=True, type='char', size=128, store=_store_product_code, string='Product Reference', readonly=True),
        # 'taxes_id': fields.function(_get_po_taxes, type='many2many', relation='account.tax', store=_store_po_taxes, string='Purchase Taxes', groups="account.group_account_user"),
        'partner_ref':  fields.related('partner_id', 'ref', string='Partner Ref', type='char', size=16),
        'picking_return':  fields.related('picking_id', 'return', string='Picking Return', type='char', size=12, readonly=1),
        'product_categ_id':  fields.related('product_id', 'categ_id', string='Product Category', type='many2one', relation='product.category',size=12, readonly=1),
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
    }
    
    def product_id_change(self, cr, uid, ids, product, location_id, location_dest_id, date_expected, context=None):
        context = context or {}
        result = {}
        
        product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
        if product_obj and product_obj.uom_id:
            result['product_uom'] = product_obj.uom_id.id
        result['name'] = product_obj.name
        result['location_id'] = location_id
        result['location_dest_id'] = location_dest_id
        result['date_expected'] = date_expected
        return {'value': result}
    
    #LY 0522 set  incoming and supplier return
    def action_done(self, cr, uid, ids, context=None):
        res=super(StockMove, self).action_done(cr, uid, ids, context=context)
        for move in self.browse(cr, uid, ids):
            if move.type == 'in' or (move.type=='out' and move.picking_return == 'supplier'):
                self.write(cr, uid, [move.id],{'date':move.picking_id.date})
        return res
    
    def action_scrap(self, cr, uid, ids, quantity, location_id, context=None):
        """ Move the scrap/damaged product into scrap location
        @param cr: the database cursor
        @param uid: the user id
        @param ids: ids of stock move object to be scrapped
        @param quantity : specify scrap qty
        @param location_id : specify scrap location
        @param context: context arguments
        @return: Scraped lines
        """
        #quantity should in MOVE UOM
        if quantity <= 0:
            raise osv.except_osv(_('Warning!'), _('Please provide a positive quantity to scrap.'))
        res = []
        for move in self.browse(cr, uid, ids, context=context):
            move_qty = move.product_qty
            uos_qty = quantity / move_qty * move.product_uos_qty
            default_val = {
                'product_qty': quantity,
                'product_uos_qty': uos_qty,
                'state': move.state,
                'scrapped' : True,
                'location_dest_id': location_id,
                'tracking_id': move.tracking_id.id,
                'prodlot_id': move.prodlot_id.id,
                'note': context and context.get('note', ''),
            }
            new_move = self.copy(cr, uid, move.id, default_val)

            res += [new_move]
            product_obj = self.pool.get('product.product')
            for product in product_obj.browse(cr, uid, [move.product_id.id], context=context):
                if move.picking_id:
                    uom = product.uom_id.name if product.uom_id else ''
                    message = _("%s %s %s has been <b>moved to</b> scrap.") % (quantity, uom, product.name)
                    move.picking_id.message_post(body=message)

        self.action_done(cr, uid, res, context=context)
        return res

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms stock move.
        @return: List of ids.
        """
        moves = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        
        new_moves=[]
        for move in moves:
            if move.location_id.usage == 'production' or move.location_id.usage == 'supplier' or move.location_dest_id.id == 11 or move.location_dest_id.id == 30: 
#TODO: temporary fix to be remove with different handling of push flows.
                new_moves.append(move)
        self.create_chained_picking(cr, uid, new_moves, context)
        return []
StockMove()

#class report_stock_inventory(osv.osv):
#    _inherit = "report.stock.inventory"
#    _name = "report.stock.inventory"
#    _auto = False
#    
#    _columns = {
#        'product_uom':   fields.many2one('product.uom', 'UoM', readonly=True),
#        'product_p_qty': fields.float('Qty in Purchase UoM',  digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
#        'product_p_uom': fields.many2one('product.uom', 'Purchase UoM', readonly=True),
#        'avg_cost':      fields.float('Average Cost',  digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True, group_operator="avg"),
#    }
#    
#    def init(self, cr):
#        tools.drop_view_if_exists(cr, 'report_stock_inventory')
#        cr.execute("""
#CREATE OR REPLACE view report_stock_inventory AS (
#    (SELECT
#        min(m.id) as id, m.date as date,
#        to_char(m.date, 'YYYY') as year,
#        to_char(m.date, 'MM') as month,
#        m.partner_id as partner_id, m.location_id as location_id,
#        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type, l.scrap_location as scrap_location,
#        m.company_id,
#        m.state as state, m.prodlot_id as prodlot_id,
#        pt.uom_id as product_uom,
#        m.product_uom as product_p_uom,
#        coalesce(sum(-pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
#        coalesce(sum(-m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty,
#        coalesce(sum(-m.product_qty)::decimal, 0.0) as product_p_qty,
#        coalesce(sum(pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) / (CASE coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) WHEN 0 THEN NULL ELSE coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) END) as avg_cost
#    FROM
#        stock_move m
#            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
#            LEFT JOIN product_product pp ON (m.product_id=pp.id)
#            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
#            LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
#            LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
#            LEFT JOIN product_uom u ON (m.product_uom=u.id)
#            LEFT JOIN stock_location l ON (m.location_id=l.id)
#    GROUP BY
#        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id,  m.location_dest_id,
#        m.prodlot_id, m.date, m.state, l.usage, l.scrap_location, m.company_id, pt.uom_id, to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
#) UNION ALL (
#    SELECT
#        -m.id as id, m.date as date,
#        to_char(m.date, 'YYYY') as year,
#        to_char(m.date, 'MM') as month,
#        m.partner_id as partner_id, m.location_dest_id as location_id,
#        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type, l.scrap_location as scrap_location,
#        m.company_id,
#        m.state as state, m.prodlot_id as prodlot_id,
#        pt.uom_id as product_uom,
#        m.product_uom as product_p_uom,
#        coalesce(sum(pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
#        coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty,
#        coalesce(sum(m.product_qty)::decimal, 0.0) as product_p_qty,
#        coalesce(sum(pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) / (CASE coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) WHEN 0 THEN NULL ELSE coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) END) as avg_cost
#    FROM
#        stock_move m
#            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
#            LEFT JOIN product_product pp ON (m.product_id=pp.id)
#            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
#            LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
#            LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
#            LEFT JOIN product_uom u ON (m.product_uom=u.id)
#            LEFT JOIN stock_location l ON (m.location_dest_id=l.id)
#    GROUP BY
#        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id, m.location_dest_id,
#        m.prodlot_id, m.date, m.state, l.usage, l.scrap_location, m.company_id, pt.uom_id, to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
#    )
#);""")
#
#report_stock_inventory()


class stock_location(osv.osv):
    _inherit = "stock.location"
    _name = "stock.location"


    def _product_get_all_report(self, cr, uid, ids, product_ids=False, context=None):
        return self._product_get_report(cr, uid, ids, product_ids, context, recursive=True)


    def _product_get_report(self, cr, uid, ids, product_ids=False,
            context=None, recursive=False):
        """ Finds the product quantity and price for particular location.
        @param product_ids: Ids of product
        @param recursive: True or False
        @return: Dictionary of values
        """
        if context is None:
            context = {}
            user = self.pool.get("res.users").browse(cr, uid, uid)
            context.update({"lang":user.partner_id and user.partner_id.lang or "en_US"})
        product_obj = self.pool.get('product.product')
        move_obj = self.pool.get('stock.move')
        # Take the user company and pricetype
        context['currency_id'] = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id

        # To be able to offer recursive or non-recursive reports we need to prevent recursive quantities by default
        context['compute_child'] = False

        if not product_ids:
            #product_ids = product_obj.search(cr, uid, [], context={'active_test': False})
            cr.execute("select distinct product_id from stock_move where state = 'done' and ( location_id IN %s or location_dest_id IN %s )", (tuple(ids), tuple(ids),))
            product_ids = filter(None, map(lambda x:x[0], cr.fetchall()))

        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_by_uom = {}
        products_by_id = {}
        for product in products:
            products_by_uom.setdefault(product.uom_id.id, [])
            products_by_uom[product.uom_id.id].append(product)
            products_by_id.setdefault(product.id, [])
            products_by_id[product.id] = product

        result = {}
        result['product'] = []
        for id in ids:
            quantity_total = 0.0
            total_price = 0.0
            for uom_id in products_by_uom.keys():
                fnc = self._product_get
                if recursive:
                    fnc = self._product_all_get
                ctx = context.copy()
                ctx['uom'] = uom_id
                qty = fnc(cr, uid, id, [x.id for x in products_by_uom[uom_id]],
                        context=ctx)
                for product_id in qty.keys():
                    if not qty[product_id]:
                        continue
                    prod_p_qty = 0
                    product = products_by_id[product_id]
                    quantity_total += qty[product_id]

                    # Compute based on pricetype
                    # Choose the right filed standard_price to read
                    amount_unit = product.price_get('standard_price', context=context)[product.id]
                    price = qty[product_id] * amount_unit

                    prod_p_qty = (qty[product_id] / product.uom_id.factor * product.uom_po_id.factor)

                    total_price += price
                    result['product'].append({
                        'price': amount_unit,
                        'prod_name': product.name_sort_en,
                        'prod_name_cn': product.name_sort_cn,
                        'code': product.default_code, # used by lot_overview_all report!
                        'variants': product.variants or '',
                        'uom': product.uom_id.name,
                        'p_uom': product.uom_po_id.name,
                        'prod_qty': qty[product_id],
                        'prod_p_qty': prod_p_qty,
                        'price_value': price,
                    })
        result['total'] = quantity_total
        result['total_price'] = total_price
        return result    

    _columns = {
        'location_return': fields.boolean(_('For Return ?'), help=_('This location is for return goods?')),
    }
    
stock_location()

class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"
    _columns = {
        'lot_return_id': fields.many2one('stock.location', 'Location For Return', domain=[('location_return', '=', 'True')]),
    }
stock_warehouse()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'last_exception': fields.text('Last Exception'),
    }
mrp_production()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
