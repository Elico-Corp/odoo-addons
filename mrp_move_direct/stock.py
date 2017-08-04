# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp.tools import float_compare,float_round
from openerp import SUPERUSER_ID
import time
import os

class stock_move_add(osv.TransientModel):
    _name = "stock.move.add"
    _description = "Add new Move for Production Order"

    _columns = {
        'date_expected': fields.datetime('Scheduled Date', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True, domain=[('type','<>','service')]),

        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True ),
        'product_uos_qty': fields.float('Quantity (UOS)', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uos': fields.many2one('product.uom', 'Product UOS'),
        'location_id': fields.many2one('stock.location', 'Source Location', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', required=True),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number'),
    }

    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        if context is None:
            context = {}
        if not context.get('mo_id', False) or not context.get('active_id', False) :
            mod_obj = self.pool.get('ir.model.data')
            location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', 'stock_location_production')
        else:
            mrp_obj = self.pool.get('mrp.production')
            production = mrp_obj.browse(cr, uid, context.get('mo_id', False) or context.get('active_id', False), context)
            location_id = production.product_id.property_stock_production.id
        return location_id

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        if context is None:
            context = {}
        return context.get('location_id', False)

    _defaults = {
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
        'product_qty': 1.0,
        'date_expected': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
                        loc_id=False, product_id=False, uom_id=False, context=None):
        """ On change of production lot gives a warning message.
        @param prodlot_id: Changed production lot id
        @param product_qty: Quantity of product
        @param loc_id: Location id
        @param product_id: Product id
        @return: Warning message
        """
        if not prodlot_id or not loc_id:
            return {}
        ctx = context and context.copy() or {}
        ctx['location_id'] = loc_id
        ctx.update({'raise-exception': True})
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product_uom = product_obj.browse(cr, uid, product_id, context=ctx).uom_id
        prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context=ctx)
        location = self.pool.get('stock.location').browse(cr, uid, loc_id, context=ctx)
        uom = uom_obj.browse(cr, uid, uom_id, context=ctx)
        amount_actual = uom_obj._compute_qty_obj(cr, uid, product_uom, prodlot.stock_available, uom, context=ctx)
        warning = {}
        if (location.usage == 'internal') and (product_qty > (amount_actual or 0.0)):
            warning = {
                'title': _('Insufficient Stock for Serial Number !'),
                'message': _('You are moving %.2f %s but only %.2f %s available for this serial number.') % (product_qty, uom.name, amount_actual, uom.name)
            }
        return {'warning': warning}

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_uos_qty': 0.00
          }
        warning = {}

        if (not product_id) or (product_qty <=0.0):
            result['product_qty'] = 0.0
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
        
        # Warn if the quantity was decreased 
        if ids:
            for move in self.read(cr, uid, ids, ['product_qty']):
                if product_qty < move['product_qty']:
                    warning.update({
                       'title': _('Information'),
                       'message': _("By changing this quantity here, you accept the "
                                "new quantity as complete: OpenERP will not "
                                "automatically generate a back order.") })
                break

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        else:
            result['product_uos_qty'] = product_qty

        return {'value': result, 'warning': warning}

    def onchange_uos_quantity(self, cr, uid, ids, product_id, product_uos_qty,
                          product_uos, product_uom):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_uos_qty: Changed UoS Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_qty': 0.00
          }
        warning = {}

        if (not product_id) or (product_uos_qty <=0.0):
            result['product_uos_qty'] = 0.0
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
        
        # Warn if the quantity was decreased 
        for move in self.read(cr, uid, ids, ['product_uos_qty']):
            if product_uos_qty < move['product_uos_qty']:
                warning.update({
                   'title': _('Warning: No Back Order'),
                   'message': _("By changing the quantity here, you accept the "
                                "new quantity as complete: OpenERP will not "
                                "automatically generate a Back Order.") })
                break

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_qty'] = product_uos_qty / uos_coeff['uos_coeff']
        else:
            result['product_qty'] = product_uos_qty
        return {'value': result, 'warning': warning}
        
    def onchange_product_id(self, cr, uid, ids, prod_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        
        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=None)[0]
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_qty': 1.00,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'prodlot_id' : False,
        }
        return {'value': result}
    
    def add_production_line_procurement(self, cr, uid, new_move, production, shipment_move_id, context=None):
        wf_service = netsvc.LocalService("workflow")
        procurement_order = self.pool.get('procurement.order')

        location_id = new_move.location_id.id or production.location_src_id.id
        date_planned = new_move.date_expected or production.date_planned
        procurement_name = (production.origin or '').split(':')[0] + ':' + production.name
        procurement_id = procurement_order.create(cr, uid, {
                    'name': procurement_name,
                    'origin': procurement_name,
                    'date_planned': date_planned,
                    'product_id': new_move.product_id.id,
                    'product_qty': new_move.product_qty,
                    'product_uom': new_move.product_uom.id,
                    'product_uos_qty': new_move.product_uos and new_move.product_qty or False,
                    'product_uos': new_move.product_uos and new_move.product_uos.id or False,
                    'location_id': location_id,
                    'procure_method': new_move.product_id.procure_method,
                    'move_id': shipment_move_id,
                    'company_id': production.company_id.id,
                })
        wf_service.trg_validate(uid, procurement_order._name, procurement_id, 'button_confirm', cr)
        wf_service.trg_validate(uid, procurement_order._name, procurement_id, 'button_check', cr)
        return procurement_id

    def add_production_internal_shipment_line(self, cr, uid, new_move, production, consume_move_id=False, context=None):
        stock_move = self.pool.get('stock.move')
        date_planned = new_move.date_expected or production.date_planned
        # Internal shipment is created for Stockable and Consumer Products
        if new_move.product_id.type not in ('product', 'consu'):
            return False
        source_location_id = new_move.location_id.id or production.location_src_id.id
        
        move_id = stock_move.create(cr, uid, {
                        'name': production.name,
                        #'picking_id': shipment_id,
                        'product_id': new_move.product_id.id,
                        'product_qty': new_move.product_qty,
                        'product_uom': new_move.product_uom.id,
                        'product_uos_qty': new_move.product_uos and new_move.product_uos_qty or False,
                        'product_uos': new_move.product_uos and new_move.product_uos.id or False,
                        'date': date_planned,
                        'date_expected': date_planned,
                        'move_dest_id': consume_move_id,
                        'location_id': source_location_id,
                        'location_dest_id': source_location_id,
                        'state': 'waiting',
                        'company_id': production.company_id.id,
                })

        if production.picking_id:
            if production.picking_id.state != 'done':
                new_move = { 'picking_id': production.picking_id.id }
            else:
                default = {}
                # SHOULD USE ir_sequence.next_by_code() or ir_sequence.next_by_id()
                default['name'] = self.pool.get('ir.sequence').get(cr, uid, production.picking_id.type)
                default['move_lines'] = False
                default['state'] = 'auto'
                new_picking = self.pool.get('stock.picking').copy(cr, uid, production.picking_id.id, default, context)
                if new_picking:
                    new_move = { 'picking_id': new_picking }
                    production.write({'picking_id':new_picking}, context=context)
            stock_move.write(cr, uid, [move_id], new_move, context)
            wf_service = netsvc.LocalService("workflow")
            if production.picking_id.state == 'done':
                wf_service.trg_validate(uid, 'stock.picking', production.picking_id.id, 'button_confirm', cr)

        return move_id

    def add_production_consume_line(self, cr, uid, new_move, production, context=None):
        stock_move = self.pool.get('stock.move')

        # Internal shipment is created for Stockable and Consumer Products
        if new_move.product_id.type not in ('product', 'consu'):
            return False
        destination_location_id = new_move.location_dest_id.id or production.product_id.property_stock_production.id
        source_location_id = new_move.location_id.id or production.location_src_id.id
        move_id = stock_move.create(cr, uid, {
            'name': production.name,
            'date': new_move.date_expected,
            'date_expected': new_move.date_expected,
            'product_id': new_move.product_id.id,
            'product_qty': new_move.product_qty,
            'product_uom': new_move.product_uom.id,
            'product_uos_qty': new_move.product_uos and new_move.product_uos_qty or False,
            'product_uos': new_move.product_uos and new_move.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': production.move_prod_id.id,
            'state': 'waiting',
            'company_id': production.company_id.id,
        })
        production.write({'move_lines': [(4, move_id)]}, context=context)
        return move_id

    def add_mo_product(self, cr, uid, ids, context=None):
        """ Add new move.
        @return: True.
        """        
        if context is None:
            context = {}
        
        if not context.get('mo_id', False) or not context.get('active_id', False) :
            raise osv.except_osv(_('Exception!'), _('Can not create the Move related to MO'))
        
        new_move = self.browse(cr, uid, ids, context)[0]
        
        mrp_obj = self.pool.get('mrp.production')
        production = mrp_obj.browse(cr, uid, context.get('mo_id', False) or context.get('active_id', False), context)

        prod_line_obj = self.pool.get('mrp.production.product.line')
        line_ids = prod_line_obj.search(cr, uid, [('production_id','=', production.id),('product_id','=', new_move.product_id.id)], context=context)
        if line_ids:
            pl = prod_line_obj.browse(cr, uid, line_ids[0]) 
            qty_in_line_uos = False           
            product_uom_obj = self.pool.get('product.uom')
            qty_in_line_uom = product_uom_obj._compute_qty(cr, uid, pl.product_uom.id, new_move.product_qty, to_uom_id=new_move.product_uom.id)
            vals={'product_qty': pl.product_qty + qty_in_line_uom}
            if pl.product_uos and new_move.product_uos and pl.product_uos_qty and new_move.product_uos_qty:
                qty_in_line_uos = product_uom_obj._compute_qty(cr, uid, pl.product_uos.id, new_move.product_uos_qty or 0.0, to_uom_id=new_move.product_uos.id)
                vals={'product_uos_qty': pl.product_uos_qty or 0.0 + qty_in_line_uos}
            prod_line_obj.write(cr, uid, [pl.id], vals)
            
            found = False
            for move in production.move_lines:
                if move.product_id.id == new_move.product_id.id:
                    vals={'product_qty': move.product_qty + qty_in_line_uom}
                    if qty_in_line_uos:
                        vals={'product_uos_qty': move.product_uos_qty or 0.0 + qty_in_line_uos}
                    self.pool.get('stock.move').write(cr, uid, [move.id], vals)
                    found = True
                    break
            consume_move_id = False
            if not found:
                consume_move_id = self.add_production_consume_line(cr, uid, new_move, production, context=context)
        else:
            line = {
                'name': new_move.product_id.name,
                'product_id': new_move.product_id.id,
                'product_qty': new_move.product_qty,
                'product_uom': new_move.product_uom.id,
                'product_uos_qty': new_move.product_uos and new_move.product_uos_qty or False,
                'product_uos': new_move.product_uos and new_move.product_uos.id or False,
                'production_id': production.id,
            }
            prod_line_obj.create(cr, uid, line)
            consume_move_id = self.add_production_consume_line(cr, uid, new_move, production, context=context)
        #shipment_id = self._make_production_internal_shipment(cr, uid, production, context=context)
        
        shipment_move_id = self.add_production_internal_shipment_line(cr, uid, new_move, production, consume_move_id, context=context)
        procurement_id = self.add_production_line_procurement(cr, uid, new_move, production, shipment_move_id, context=context)
        self.pool.get('procurement.order').write(cr, uid, [procurement_id], {'close_move':  True}, context=context)
        
        return True
stock_move_add()

class stock_move(osv.Model):
    _inherit = "stock.move"
    
    _columns = {
        'cal_cost': fields.boolean('Calculated Cost'),
    }
    _defaults = {
        'cal_cost': False,
    }   
    #
    # Cancel move => cancel others move and pickings
    #
    def action_consume_cancel(self, cr, uid, ids, context=None):
        """ Cancels the moves and if all moves are cancelled it cancels the picking.
        @return: True
        """
        if not ids:
            return True
        
        new_move = self.browse(cr, uid, ids, context)[0]
        
        sm_ids = self.search(cr, uid, [('move_dest_id','=', new_move.id)], context=context)
        sp_picking = False
        if sm_ids:
            for move in self.browse(cr, uid, sm_ids):
                sp_picking = move.picking_id
                if move.state == 'done':
                    self.write(cr, uid, [move.id], {'state': 'cancel'})
                else:
                    self.action_cancel(cr, uid, [move.id], context=context)
        if sp_picking:            
            mrp_obj = self.pool.get('mrp.production')
            mo_ids = mrp_obj.search(cr, uid, [('picking_id','=', sp_picking.id)], context=context)
            if mo_ids:
                prod_line_obj = self.pool.get('mrp.production.product.line')
                ml_ids = prod_line_obj.search(cr, uid, [('production_id','=', mo_ids[0]),('product_id','=', new_move.product_id.id)], context=context)
                if ml_ids:
                    prod_line = prod_line_obj.browse(cr, uid, ml_ids)[0]
                    compare = float_compare(prod_line.product_qty, new_move.product_qty, precision_rounding=4)
                    if compare == 0:
                        prod_line_obj.unlink(cr, uid, [prod_line.id], context=context)
                    elif compare > 0:
                        prod_line_obj.write(cr, uid, [prod_line.id], {'product_qty': prod_line.product_qty - new_move.product_qty})
                    
        self.action_cancel(cr, uid, [new_move.id], context=context)

stock_move()

class mrp_production(osv.osv):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'

    _columns = {
        'move_lines2': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Consumed Products',
            domain=[('state','in', ('done',''))], readonly=True, states={'draft':[('readonly',False)]}),
    }

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
        
        #LY Start COPY from standard add rounding in 0510
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce
        @param production_mode: specify production mode (consume/consume&produce).
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)

        produced_qty = 0
        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or (produced_product.product_id.id != production.product_id.id):
                continue
            produced_qty += produced_product.product_qty
        if production_mode in ['consume','consume_produce']:
            consumed_data = {}

            # Calculate already consumed qtys
            for consumed in production.move_lines2:
                if consumed.scrapped:
                    continue
                if not consumed_data.get(consumed.product_id.id, False):
                    consumed_data[consumed.product_id.id] = 0
                consumed_data[consumed.product_id.id] += consumed.product_qty

            # Find product qty to be consumed and consume it
            for scheduled in production.product_lines:

                # total qty of consumed product we need after this consumption
                total_consume = ((production_qty + produced_qty) * scheduled.product_qty / production.product_qty)

                # qty available for consume and produce
                qty_avail = scheduled.product_qty - consumed_data.get(scheduled.product_id.id, 0.0)

                if qty_avail <= 0.0:
                    # there will be nothing to consume for this raw material
                    continue

                raw_product = [move for move in production.move_lines if move.product_id.id==scheduled.product_id.id]
                if raw_product:
                    # qtys we have to consume
                    qty = total_consume - consumed_data.get(scheduled.product_id.id, 0.0)
                    if float_compare(qty, qty_avail, precision_rounding=scheduled.product_id.uom_id.rounding) == 1:
                        # if qtys we have to consume is more than qtys available to consume
                        prod_name = scheduled.product_id.name_get()[0][1]
                        raise osv.except_osv(_('Warning!'), _('You are going to consume total %s quantities of "%s".\nBut you can only consume up to total %s quantities.') % (qty, prod_name, qty_avail))
                    if qty <= 0.0:
                        # we already have more qtys consumed than we need
                        continue

                    qty = round(qty,3)#LY 0510
                    raw_product[0].action_consume(qty, raw_product[0].location_id.id, context=context)

        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            #vals = {'state':'confirmed'}
            #final_product_todo = [x.id for x in production.move_created_ids]
            #stock_mov_obj.write(cr, uid, final_product_todo, vals)
            #stock_mov_obj.action_confirm(cr, uid, final_product_todo, context)
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty

            for produce_product in production.move_created_ids:
                produced_qty = produced_products.get(produce_product.product_id.id, 0)
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                rest_qty = (subproduct_factor * production.product_qty) - produced_qty

                if rest_qty < production_qty:
                    prod_name = produce_product.product_id.name_get()[0][1]
                    raise osv.except_osv(_('Warning!'), _('You are going to produce total %s quantities of "%s".\nBut you can only produce up to total %s quantities.') % (production_qty, prod_name, rest_qty))
                if rest_qty > 0 :
                    stock_mov_obj.action_consume(cr, uid, [produce_product.id], (subproduct_factor * production_qty), context=context)

        for raw_product in production.move_lines2:
            new_parent_ids = []
            parent_move_ids = [x.id for x in raw_product.move_history_ids]
            for final_product in production.move_created_ids2:
                if final_product.id not in parent_move_ids:
                    new_parent_ids.append(final_product.id)
            for new_parent_id in new_parent_ids:
                stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce_done', cr)
        
        
        #LY END COPY
        #if super(mrp_production, self).action_produce(cr, uid, production_id, production_qty, production_mode, context=context):
        if production_mode == 'consume':
            return True
        move_obj = self.pool.get('stock.move')
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        plan_obj = self.pool.get('procurement.order')
        production = self.browse(cr, uid, production_id, context=context)
        if production.product_id.cost_method == 'standard':
            return True

        sm_ids = move_obj.search(cr, uid, [('name','=', production.name), ('state', '!=', 'done'), ('move_dest_id', '!=', False)], context=context)
        if sm_ids:                
            plan_ids = plan_obj.search(cr, uid, [('move_id','in', sm_ids)], context=context)
            plan_obj.action_done(cr, uid, plan_ids)

        cost_price = 0.0
        for move in production.move_lines2:
            if move.scrapped or move.state == 'cancel' or move.cal_cost:
                continue
            vals = {'cal_cost': True}
            if not move.price_unit:
                if move.product_uom.id == move.product_id.uom_id.id:
                    price_unit = move.product_id.standard_price
                else:                        
                    default_uom = move.product_id.uom_id.id
                    price_unit = product_uom_obj._compute_price(cr, uid, default_uom, move.product_qty, move.product_uom.id)
                vals['price_unit'] = price_unit
            else:
                price_unit = move.price_unit
            move_obj.write(cr, uid, [move.id], vals, context=context)
            cost_price += (move.product_qty * price_unit)
        
        qty_available = production.product_id.qty_available
        total_prod = 0.0
        for prod_id in production.move_created_ids2:
            if prod_id.product_uom.id == prod_id.product_id.uom_id.id:
                total_prod += prod_id.product_qty
            else:                        
                total_prod += prod_id.product_qty * prod_id.product_id.product_uom.factor * prod_id.product_uom.factor
        
        compare = float_compare(qty_available, 0.0, precision_rounding=4)
        if compare == 0:
            price_unit = cost_price / production_qty
        else:
            price_unit = ((qty_available - production_qty) * production.product_id.standard_price + cost_price ) / (qty_available)
        #price_unit = ( qty_available * production.product_id.standard_price + cost_price) / (qty_available + production_qty)
        digits = self.pool.get('decimal.precision').precision_get(cr, SUPERUSER_ID, 'Product Price')
        price_unit = float_round(price_unit, precision_digits=digits)
        move_ids = [ move.id for move in production.move_created_ids2 if not move.price_unit]
        move_obj.write(cr, uid, move_ids, {'price_unit':  price_unit}, context=context)
        product_obj.write(cr, uid, [production.product_id.id], {'standard_price': price_unit}, context=context)
        
        return True

class move_scrap_directly(osv.TransientModel):
    _name = "move.scrap.directly"
    _description = "Scrap Products"
    #_inherit = "stock.move.consume"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
        'location_id': fields.many2one('stock.location', 'Location', required=True)
    }

    _defaults = {
        'location_id': lambda *x: False
    }

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        res = super(move_scrap_directly, self).default_get(cr, uid, fields, context=context)
        move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
        location_obj = self.pool.get('stock.location')
        scrpaed_location_ids = location_obj.search(cr, uid, [('scrap_location','=',True)])

        if 'product_id' in fields:
            res.update({'product_id': move.product_id.id})
        if 'product_uom' in fields:
            res.update({'product_uom': move.product_uom.id})
        if 'product_qty' in fields:
            res.update({'product_qty': move.product_qty})
        if 'location_id' in fields:
            if scrpaed_location_ids:
                res.update({'location_id': scrpaed_location_ids[0]})
            else:
                res.update({'location_id': False})

        return res

    def move_scrap_dir(self, cr, uid, ids, context=None):
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
            move_obj.write(cr, uid, move_ids,
                {'location_dest_id': data.location_id.id}, context=context)
            move_obj.action_done(cr, uid, move_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
move_scrap_directly()

class return_scrap_directly(osv.TransientModel):
    _name = "return.scrap.directly"
    _description = "Scrap Return Products"

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'return_comment': fields.text('From Return Location Moves'),
        'not_comment': fields.text('Not From Return Locations'),
    }

    _defaults = {
        'location_id': lambda *x: False
    }

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        res = super(return_scrap_directly, self).default_get(cr, uid, fields, context=context)
        moves = self.pool.get('stock.move').browse(cr, uid, context['active_ids'], context=context)
        location_obj = self.pool.get('stock.location')
        scrpaed_location_ids = location_obj.search(cr, uid, [('scrap_location','=',True)])

        if 'location_id' in fields:
            if scrpaed_location_ids:
                res.update({'location_id': scrpaed_location_ids[0]})
            else:
                res.update({'location_id': False})

        return_move = _('Exclude the done or cancel Moves:')
        not_return_move = _('Exclude the done or cancel Moves:')
        for move in moves:
            if move.state in ('done','cancel'):
                continue
            if move.location_id.location_return:
                return_move = os.linesep.join([return_move, '-'.join([move.name, move.product_id.name or '', move.location_id.name, move.location_dest_id.name])])
            else:
                not_return_move = os.linesep.join([not_return_move, '-'.join([move.name, move.product_id.name or '', move.location_id.name, move.location_dest_id.name])])

        if 'return_comment' in fields:
            res.update({'return_comment': return_move})
        if 'not_comment' in fields: 
            res.update({'not_comment': not_return_move})

        return res

    def move_scrap_dir(self, cr, uid, ids, context=None):
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
        move_ids = []
        for move in move_obj.browse(cr, uid, context['active_ids'], context=context):
            if move.state not in ('done','cancel') and move.location_id.location_return:
                move_ids.append(move.id)
        if move_ids:
            for data in self.browse(cr, uid, ids):
                move_obj.write(cr, uid, move_ids,
                               {'location_dest_id': data.location_id.id}, context=context)
                move_obj.action_done(cr, uid, move_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
return_scrap_directly()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: