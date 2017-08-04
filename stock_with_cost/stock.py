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

class StockPicking(osv.osv):
    _inherit = 'stock.picking'
    
#    def search(self, cr, uid, args, offset=0, limit=None, order='name', context=None, count=False):
#        new_args = []
#        for arg in args:
#            if len(arg)==3 and arg[0]=='name':
#                new_args.append('|')
#                new_args.append(('origin',arg[1],arg[2]))
#            new_args.append(arg)
#        return super(StockPicking, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
    def _calcul_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        
        move_pool = self.pool.get('stock.move')
        
        for pick in self.browse(cr, uid, ids, context=context):
            amount = 0
            amount_to_receive =0
            move_ids = move_pool.search(cr, uid, [('picking_id', '=', pick.id), ('state','=','done')])
            for move in move_pool.read(cr, uid, move_ids, ['po_price','product_qty']):
                amount += move['po_price'] * move['product_qty']
            toreceive_ids = move_pool.search(cr, uid, [('picking_id', '=', pick.id), ('state','in',('assigned','confirmed','waiting','draft'))])
            for move in move_pool.read(cr, uid, toreceive_ids, ['po_price','product_qty']):
                amount_to_receive += move['po_price'] * move['product_qty']
            res[pick.id] = {'amount_to_receive':amount_to_receive,
                            'amount_received':amount,
                            'amount_total':amount + amount_to_receive}
        return res

    def _move_state_change(self, cr, uid, ids, context=None):
        picking_ids = []
        picking_pool = self.pool.get('stock.picking')
        picking_ids = self.read(cr, uid, ids, ['picking_id'], context=context)
        picking_ids = list(set([ move['picking_id'] and move['picking_id'][0] for move in picking_ids]))
        return picking_ids

    _store_amount={
        'stock.picking.in': (lambda self, cr, uid, ids, context: ids, ['state'], 10),
        'stock.move': (_move_state_change, ['state','product_qty','picking_id','po_price','amount_total'], 10),
    }
    
    _columns = {
        'amount_received': fields.function(_calcul_amount, type='float', string='Amount Received', digits_compute=dp.get_precision('Account'),
                                           store=_store_amount,multi='sums'), 
        'amount_to_receive': fields.function(_calcul_amount, type='float', string='Amount To Receive', digits_compute=dp.get_precision('Account'),
                                             store=_store_amount,multi='sums'),
        'amount_total': fields.function(_calcul_amount, type='float', string='Amount Total', digits_compute=dp.get_precision('Account'),
                                             store=_store_amount,multi='sums'),
    }

StockPicking()


class StockPickingIn(osv.osv):
    _inherit = 'stock.picking.in'
    
#    def _auto_init(self, cr, context=None):
#        super(StockPickingIn, self)._auto_init(cr, context)
#        #cr.execute("SELECT id FROM product_product WHERE name IS NULL")
#        cr.execute("SELECT id FROM stock_picking WHERE type = 'in' AND ( amount_to_receive IS NULL OR amount_received IS NULL) ")
#        picking_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
#        for picking in self.browse(cr, 1, picking_ids):
#            self.write(cr, 1, picking.id, {
#                                           'amount_to_receive':picking.amount_to_receive, # TO BE REMOVED AFTER THE amount_to_receive FIELDS 1ST CALCULATION
#                                           'amount_received':picking.amount_received})# TO BE REMOVED AFTER THE amount_received FIELDS 1ST CALCULATION
    
    def _calcul_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        
        move_pool = self.pool.get('stock.move')
        
        for pick in self.browse(cr, uid, ids, context=context):
            amount = 0
            amount_to_receive =0
            move_ids = move_pool.search(cr, uid, [('picking_id', '=', pick.id), ('state','=','done')])
            for move in move_pool.read(cr, uid, move_ids, ['po_price','product_qty']):
                amount += move['po_price'] * move['product_qty']
            toreceive_ids = move_pool.search(cr, uid, [('picking_id', '=', pick.id), ('state','in',('assigned','confirmed','waiting','draft'))])
            for move in move_pool.read(cr, uid, toreceive_ids, ['po_price','product_qty']):
                amount_to_receive += move['po_price'] * move['product_qty']
            res[pick.id] = {'amount_to_receive':amount_to_receive,
                            'amount_received':amount,
                            'amount_total':amount + amount_to_receive}
        return res
        
    def _move_state_change(self, cr, uid, ids, context=None):
        picking_ids = []
        picking_pool = self.pool.get('stock.picking')
        picking_ids = self.read(cr, uid, ids, ['picking_id'], context=context)
        picking_ids = list(set([ move['picking_id'] and move['picking_id'][0] for move in picking_ids]))
        picking_ids = picking_pool.search(cr, uid, ['&',('id','in',picking_ids),'|','&',('type','=','in'),('return','=','none'),'&',('type','=','out'),('return','=','supplier')])
        return picking_ids
    
    _store_amount={
        'stock.picking.in': (lambda self, cr, uid, ids, context: ids, ['state','move_lines'], 10),
        'stock.move': (_move_state_change, ['product_qty','po_price','amount_total'], 10),
    }
    
        
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    _columns = {    
        'amount_received': fields.function(_calcul_amount, type='float', string='Amount Received', digits_compute=dp.get_precision('Account'),
                                           store=_store_amount,multi='sums'), 
        'amount_to_receive': fields.function(_calcul_amount, type='float', string='Amount To Receive', digits_compute=dp.get_precision('Account'),
                                             store=_store_amount,multi='sums'),
        'amount_total': fields.function(_calcul_amount, type='float', string='Amount Total', digits_compute=dp.get_precision('Account'),
                                             store=_store_amount,multi='sums'),
    }

StockPickingIn()

class StockMove(osv.osv):
    _inherit = 'stock.move'
        
    def _move_to_update_folowing_pol_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('stock.move').search(cr, uid, [('purchase_line_id', 'in', ids)]) or []
    
    def _get_po_price(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
            price = move.purchase_line_id and move.purchase_line_id.price_unit or False
            if price and move.picking_return == 'supplier':
                price = -price
            result[move.id] = price
        return result
    
    def _po_price_inv(self, cr, uid, id, name, value, arg, context=None):
        if value and id:
            cr.execute("UPDATE stock_move SET %s = '%s' WHERE id = %s" % (name, value, id))
        return True
    
    _store_po_price={
        'stock.move': (lambda self, cr, uid, ids, context: ids, ['purchase_line_id'], 8),
    }
    
    def _get_po_subtotal(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
            result[move.id] =  move.po_price * move.product_qty or False
        return result
    
    _store_amount_total={
        'stock.move': (lambda self, cr, uid, ids, context: ids, ['po_price','product_qty','product_id'], 10),
    }
    
    _columns = {
        'po_price':  fields.function(_get_po_price, fnct_inv=_po_price_inv, method=True, type='float', digits_compute=dp.get_precision('Product Price'), store=_store_po_price, string='Purchase Price'),
        'amount_total':  fields.function(_get_po_subtotal, method=True, type='float', digits_compute=dp.get_precision('Account'), store=_store_amount_total, string='Subtotal'),
    }

    def _auto_init(self, cr, context=None):
       super(StockMove, self)._auto_init(cr, context)
       cr.execute("SELECT id FROM stock_move WHERE purchase_line_id is NOT NULL AND ( po_price IS NULL OR amount_total IS NULL) ")
       move_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
       for move in self.browse(cr, 1, move_ids):
           self.write(cr, 1, move.id, {
                                          'po_price':move.po_price,
                                          'amount_total':move.amount_total,})
StockMove()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
