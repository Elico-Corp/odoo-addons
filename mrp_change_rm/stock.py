# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp.tools import float_compare
import time

class stock_move_add(osv.osv_memory):
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
                default['name'] = self.pool.get('ir.sequence').get(cr, uid, production.picking_id.type)
                default['move_line'] = False
                default['state'] = 'auto'
                new_picking = self.pool.get('stock.picking').copy(cr, uid, production.picking_id.id, default, context)
                if new_picking:
                    new_move = { 'picking_id': new_picking }
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
        self.add_production_line_procurement(cr, uid, new_move, production, shipment_move_id, context=context)
        
        
        return True
stock_move_add()

class stock_move(osv.osv):
    _inherit = "stock.move"
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

class mrp_production(osv.osv):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'

    _columns = {
        'move_lines2': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Consumed Products',
            domain=[('state','in', ('done',''))], readonly=True, states={'draft':[('readonly',False)]}),
    }
