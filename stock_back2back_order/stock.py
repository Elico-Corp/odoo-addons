# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author: Ian Li <ian.li@elico-corp.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import netsvc
import tools

class stock_location(osv.osv):
    _inherit = "stock.location"
    
    def picking_type_get(self, cr, uid, from_location, to_location, context=None):
        """ Gets type of picking.
        @param from_location: Source location
        @param to_location: Destination location
        @return: Location type
        """
        result = 'internal'
        if (from_location.usage=='internal') and (to_location and to_location.usage in ('customer', 'supplier')):
            result = 'out'
        elif (from_location.usage in ('supplier', 'customer')) and (to_location.usage in ('internal', 'supplier')): # Also consider inter-supplier picking as IN. Ian@Elico 
            result = 'in'
        return result
    _columns = {
        'chained_auto_packing': fields.selection(
            [('auto', 'Automatic Move'),('semi-auto', 'Back-to-back Move'), ('manual', 'Manual Operation'), ('transparent', 'Automatic No Step Added')],
            'Chaining Type',
            required=True,
            help="This is used only if you select a chained location type.\n" \
                "The 'Automatic Move' value will create a stock move after the current one that will be "\
                "validated automatically. With 'Manual Operation', the stock move has to be validated "\
                "by a worker. With 'Automatic No Step Added', the location is replaced in the original move."
            ),
    }
    _defaults = {
        'chained_auto_packing': 'manual',
    }

stock_location()

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    
    _columns = {
        'chained_picking_id': fields.many2one('stock.picking', 'Chained Picking created by create_chained_picking()', help="The chained picking created by calling create_chained_picking upon this picking.", select=True), #Ian@Elico
    }
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ We need to change the usser_id in the invoice generated.
        """
        invoice_obj = self.pool.get('account.invoice')
        
        result = super(stock_picking, self).action_invoice_create(cr, uid,
                ids, journal_id=journal_id, group=group, type=type,
                context=context)

        invoiced_pickings_to_check = result.keys()
        
        for invoiced_picking in self.browse(cr, uid, invoiced_pickings_to_check, context=context):
            for invoice_to_write in invoice_obj.browse(cr, uid, [result[invoiced_picking.id]], context=context):
                if invoice_to_write.type in ('out_invoice', 'out_refund'):
                    user_id = invoiced_picking.sale_id.user_id.id # out_invoice will use SO's salesman information. Ian@Elico
                else:
                    user_id = invoiced_picking.purchase_id.create_uid.id # in_invoice will use PO's creator information. Ian@Elico
                
                vals_to_write = {
                    'user_id': user_id
                }
                invoice_obj.write(cr, uid, [invoice_to_write.id], vals_to_write, context=context)
        return result

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few, new_chained_move_ids = [], [], [], []
            move_product_qty = {}
            prodlot_ids = {}
            product_avail = {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                #Commented in order to process the less number of stock moves from partial picking wizard
                #assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
                product_qty = partial_data.get('product_qty') or 0.0
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom') or False
                product_price = partial_data.get('product_price') or 0.0
                product_currency = partial_data.get('product_currency') or False
                prodlot_id = partial_data.get('prodlot_id') or False
                prodlot_ids[move.id] = prodlot_id
                if move.product_qty == product_qty:
                    complete.append(move)
                elif move.product_qty > product_qty:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})


            for move in too_few:
                product_qty = move_product_qty[move.id]

                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                'move_lines' : [],
                                'state':'draft',
                                'chained_picking_id' : False, # Skip Chained Picking. Ian@Elico
                            })
                if product_qty != 0: # We need to treat zero moves separately. Ian@Elico
                    defaults = {
                            'product_qty' : move.product_qty - product_qty,
                            'product_uos_qty': move.product_qty - product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'next_move': False, # No next move. Ian@Elico
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    new_chained_move_id = move_obj.copy(cr, uid, move.id, defaults)
                    new_chained_move_ids.append(new_chained_move_id) # Prepare the List for creating an new chained picking, by copying of the old move with updated DEFAULTS. Ian@Elico
                    
                    # Update the destination move quantity of old ones with the quantity actually moved, it SHOULD BE RECURSIVE but STOP at the Boundary of PO and SO. Ian@Elico
                    dest_move = move.move_dest_id
                    while dest_move and (move.sale_line_id == dest_move.sale_line_id or move.purchase_line_id == dest_move.purchase_line_id ):
                        move_obj.write(cr, uid, [dest_move.id],
                                {
                                    'product_qty' : product_qty,
                                    'product_uos_qty': product_qty,
                                })
                        dest_move = dest_move.move_dest_id
                        # TODO: Make sure the updated destination move as done. Ian@Elico
                        #complete.append(self.browse(cr, uid, move.move_dest_id, context=context))
    
                    move_obj.write(cr, uid, [move.id],
                            {
                                'product_qty' : product_qty,
                                'product_uos_qty': product_qty, #TODO: put correct uos_qty
                                'next_move': new_chained_move_id,
                            })
                elif product_qty == 0: # For something is not moved, first unlink all the existing chained moves RECURSIVELY, then put it in the new picking. Ian@Elico
                    if move.move_dest_id: # Set all the existing chained moves to cancel and unlink them from pickings if existing. Ian@Elico
                        dest_move = move.move_dest_id
                        fore_move_id = move.id
                        while dest_move and (move.sale_line_id == dest_move.sale_line_id or move.purchase_line_id == dest_move.purchase_line_id ):
                            move_obj.write(cr, uid, [dest_move.id],
                            {
                                'state' : 'cancel',
                                # 'picking_id': False, Refer to the discuss on 2012-04-12, we no longer cancel the link between the picking and the move.
                                'note': 'Cancelled by back order, origin from %s, was in picking %d, follow move %d, with note:"%s".' % (dest_move.picking_id.origin, dest_move.picking_id.id, fore_move_id, dest_move.note),
                            })
                            fore_move_id = dest_move.id
                            dest_move = dest_move.move_dest_id
                    move_obj.write(cr, uid, [move.id],
                            {
                            'picking_id' : new_picking,
                            'move_dest_id': False,
                            }) # Updating the related picking and chaining information. Ian@Elico
                    new_chained_move_ids.append(move.id) # Use it to create the new chained picking. Ian@Elico
    
            
            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': pick.id}) #Put completed move in old picking. Ian@Elico
            for move in complete:
                if prodlot_ids.get(move.id):
                    move_obj.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids[move.id]})
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                # We don't care the over moved one, let remain in the old completed picking. Ian@Elico
                #if new_picking:
                #    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)


            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [new_picking], {'backorder_id': pick.id}) # Make the new picking back order of the old one. Ian@Elico
                self.action_move(cr, uid, [pick.id]) # Change the move of the old on as assigned as following. Ian@Elico
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr) # Mark the old one done. Ian@Elico
                wf_service.trg_write(uid, 'stock.picking', new_picking, cr) # Change the status of the new picking. Ian@Elico
                delivered_pack_id = pick.id # Mark the old one delivered. Ian@Elico
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id
            
            # Create new chained picking based on those remaining partial moves. Ian@Elico
            if len(new_chained_move_ids) > 0 :
                new_chained_moves = move_obj.browse(cr, uid, new_chained_move_ids, context=context)
                move_obj.create_chained_picking(cr, uid, new_chained_moves, context)

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

stock_picking()

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    _columns = {
        'next_move': fields.many2one('stock.move', 'ID of the new move in new backorder picking.', help="The move in the picking use the old one as backorder.", select=True), # Ian@Elico
    }
    
    def _create_chained_picking(self, cr, uid, pick_name, picking, ptype, move, context=None):
        res_obj = self.pool.get('res.company')
        picking_obj = self.pool.get('stock.picking')
        # Populate the backorder info in new chained picking. Ian@Elico
        backorder_id = False
        if picking.backorder_id:
            backorder_id = picking.backorder_id.chained_picking_id.id
        # We shall also populate the sale_id or purchase_id if they existed. Ian@Elico
        defaults = {
                        'name': pick_name,
                        'origin': tools.ustr(picking.origin or ''),
                        'type': ptype,
                        'note': picking.note,
                        'move_type': picking.move_type,
                        'auto_picking': move[0][1][1] == 'auto',
                        'stock_journal_id': move[0][1][3],
                        'company_id': move[0][1][4] or res_obj._company_default_get(cr, uid, 'stock.company', context=context),
                        'address_id': picking.address_id.id,
                        'invoice_state': 'none',
                        'date': picking.date,
                        'backorder_id': backorder_id, # Append backorder_id. Ian@Elico
                    }
        if picking.sale_id : defaults['sale_id'] = picking.sale_id.id
        if picking.purchase_id : defaults['purchase_id'] = picking.purchase_id.id
        pick_id= picking_obj.create(cr, uid, defaults)
        return pick_id
    def create_chained_picking(self, cr, uid, moves, context=None):
        res_obj = self.pool.get('res.company')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        wf_service = netsvc.LocalService("workflow")
        new_moves = []
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        for picking, todo in self._chain_compute(cr, uid, moves, context=context).items():
            ptype = todo[0][1][5] and todo[0][1][5] or location_obj.picking_type_get(cr, uid, todo[0][0].location_dest_id, todo[0][1][0])
            if picking:
                # name of new picking according to its type
                new_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + ptype)
                pickid = self._create_chained_picking(cr, uid, new_pick_name, picking, ptype, todo, context=context)
                # Need to check name of old picking because it always considers picking as "OUT" when created from Sale Order
                old_ptype = location_obj.picking_type_get(cr, uid, picking.move_lines[0].location_id, picking.move_lines[0].location_dest_id)
                if old_ptype != picking.type:
                    old_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + old_ptype)
                    picking_obj.write(cr, uid, [picking.id], {'name': old_pick_name, 'type': old_ptype}, context=context) # Keep the Internal Type. Ian@Elico
            else:
                pickid = False
            for move, (loc, dummy, delay, dummy, company_id, ptype) in todo:
                # We will add the delay of dest location. Ian@Elico
                newdate = (datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') + relativedelta(days=move.location_dest_id.chained_delay or 0)).strftime('%Y-%m-%d')
                new_id = move_obj.copy(cr, uid, move.id, {
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': loc.id,
                    'date_moved': time.strftime('%Y-%m-%d'),
                    'date_expected': newdate, # New Expected Date. Ian@Elico
                    'picking_id': pickid,
                    'state': 'waiting',
                    'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', context=context)  ,
                    'move_history_ids': [],
                    'date': (datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') + relativedelta(days=delay or 0)).strftime('%Y-%m-%d'),
                    'move_history_ids2': []}
                )
                move_obj.write(cr, uid, [move.id], {
                    'move_dest_id': new_id,
                    'move_history_ids': [(4, new_id)]
                })
                new_moves.append(self.browse(cr, uid, [new_id])[0])
            if pickid:
                picking_obj.write(cr, uid, [picking.id], {'chained_picking_id': pickid }, context=context) # Add the chained picking information. Ian@Elico
                wf_service.trg_validate(uid, 'stock.picking', pickid, 'button_confirm', cr)
        if new_moves:
            new_moves += self.create_chained_picking(cr, uid, new_moves, context)
        return new_moves
    
    
    def copy_move_chain(self, cr, uid, move_id, context=None):
        '''Recursively copy the chained move.
        @return id of the new first move.
        '''
        move_tbc = self.browse(cr, uid, move_id, context)
        move_dest_id = False
        if move_tbc.move_dest_id: # If there is move_dest_id in the chain, we need to make a copy of that, then use it as new move_dest_id.
            move_dest_id = self.copy_move_chain(cr, uid, move_tbc.move_dest_id.id, context)        
        
        new_note = ((move_tbc.note if move_tbc.note else '') + ' Copy of stock.move[%d].') % move_id 
        new_move_id = self.copy(cr, uid, move_id, {
                                                   'move_dest_id': move_dest_id,
                                                   'state': move_tbc.state, # We need the state of target move, or it will be in 'Draft' by defauly.
                                                   'note': new_note,
                                                   'move_history_ids': False, # Don't inherit child, populate it in next step. The same to next line.
                                                   'move_history_ids2': False,
                                                   })
        
        if move_dest_id: # Create the move_history_ids (child) if there is.
            self.write(cr, uid, [new_move_id], {'move_history_ids': [(4, move_dest_id)]})
        return new_move_id
    
    def update_move_chain(self, cr, uid, move_id, vals, context=None):
        '''Recursively update the chained move by the first move id.
        @return True if ok.
        '''
        ids = [move_id]
        move_tbu = self.browse(cr, uid, move_id, context)
        while move_tbu.move_dest_id:
            ids.append(move_tbu.move_dest_id.id)
            move_tbu = move_tbu.move_dest_id
        self.write(cr, uid, ids, vals, context)
        return True
        
    def check_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        @return: No. of moves done
        
        !!! Caution: This method is also overridden in module product_lot_foundry. !!!
        Here we need to do some modification to the official logic: Instead of only splitting the moves inside the picking, we need to split all the remaining move chain.
        
        """
        done = []
        count = 0
        pickings = {}
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.product_id.type == 'consu' or move.location_id.usage == 'supplier':
                if move.state in ('confirmed', 'waiting'):
                    done.append(move.id)
                pickings[move.picking_id.id] = 1
                continue
            if move.state in ('confirmed', 'waiting'):
                # Important: we must pass lock=True to _product_reserve() to avoid race conditions and double reservations
                res = self.pool.get('stock.location')._product_reserve(cr, uid, [move.location_id.id], move.product_id.id, move.product_qty, {'uom': move.product_uom.id}, lock=True)
                if res:
                    #_product_available_test depends on the next status for correct functioning
                    #the test does not work correctly if the same product occurs multiple times
                    #in the same order. This is e.g. the case when using the button 'split in two' of
                    #the stock outgoing form
                    self.write(cr, uid, [move.id], {'state':'assigned'})
                    done.append(move.id)
                    pickings[move.picking_id.id] = 1
                    r = res.pop(0)
                    # We had to rewrite following line because it do not update the chain.
                    #cr.execute('update stock_move set location_id=%s, product_qty=%s, product_uos_qty=%s where id=%s', (r[1], r[0], r[0] * move.product_id.uos_coeff, move.id))
                    self.write(cr, uid, [move.id], {'location_id': r[1]})
                    self.update_move_chain(cr, uid, move.id, {'product_qty': r[0],'product_uos_qty': r[0] * move.product_id.uos_coeff})
                    

                    # Here we start to copy the whole remaining chain, and then
                    # rewrite the location of the first move, and
                    # the quantity of the chain. Ian@Elico
                    while res:
                        r = res.pop(0)
                        move_id = self.copy_move_chain(cr, uid, move.id)
                        self.write(cr, uid, [move_id], {'location_id': r[1]})
                        self.update_move_chain(cr, uid, move_id, {'product_qty': r[0],'product_uos_qty': r[0] * move.product_id.uos_coeff})
                        done.append(move_id)
        if done:
            count += len(done)
            self.write(cr, uid, done, {'state': 'assigned'})

        if count:
            for pick_id in pickings:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
        return count    
    
stock_move()