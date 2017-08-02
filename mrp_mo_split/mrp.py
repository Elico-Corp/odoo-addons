# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2009 Albert Cervera i Areny - NaN  (http://www.nan-tic.com) All Rights Reserved.
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

from datetime import datetime

from osv import osv
from osv import fields
from tools.translate import _
import netsvc

class mrp_routing_workcenter(osv.osv):
    _inherit = 'mrp.routing.workcenter'
    _order = "routing_id,sequence"
mrp_routing_workcenter()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _change_prod_qty(self, cr, uid, id ,quantity, context):

        prod_obj = self.pool.get('mrp.production')
        move_lines_obj = self.pool.get('stock.move')
        prod = prod_obj.browse(cr, uid, id , context=context)
#Andy Remove
        prod_obj.action_compute(cr, uid, [prod.id])
        for move in prod.move_lines:
            bom_point = prod.bom_id
            bom_id = prod.bom_id.id
            if not bom_point:
                bom_id = self.pool.get('mrp.bom')._bom_find(cr, uid, prod.product_id.id, prod.product_uom.id)
                if not bom_id:
                    raise osv.except_osv(_('Error'), _("Couldn't find bill of material for product"))
                self.write(cr, uid, [prod.id], {'bom_id': bom_id})
                bom_point = self.pool.get('mrp.bom').browse(cr, uid, [bom_id])[0]

            if not bom_id:
                raise osv.except_osv(_('Error'), _("Couldn't find bill of material for product"))

            factor = prod.product_qty * prod.product_uom.factor / bom_point.product_uom.factor
            res = self.pool.get('mrp.bom')._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, [])
            for r in res[0]:
                if r['product_id']== move.product_id.id:
                    move_lines_obj.write(cr, uid,move.id, {'product_qty' :  r['product_qty'], 'product_uos_qty' : False, 'product_uos':False })

        #Andy, Recalculate the Cycles and Times
        cal_val = {'hour_total':0, 'cycle_total':0}
        for wc in prod.workcenter_lines:
            cal_val['hour_total'] += wc.hour
            cal_val['cycle_total'] += wc.cycle        
        self.write(cr, uid, [prod.id], cal_val)

        for m in prod.move_created_ids:
            move_lines_obj.write(cr, uid,m.id, {'product_qty' : quantity})

        return {}

    def _update_picking( self,cr,uid,id,try_assign=False, context=None ):
        if context == None:
            context={}

        prod = self.browse(cr,uid,id,context=context)

        cancel_moves =  [x.id for x in prod.picking_id.move_lines]
        lines = []
        for move_line in  prod.move_lines:
            new_mome_id = self.pool.get('stock.move').copy(cr,uid, move_line.id, {'location_dest_id':prod.location_src_id.id, 'picking_id':prod.picking_id.id,'state':'confirmed'}, context = context)
            lines.append(new_mome_id)
        #self.pool.get('stock.picking').browse(cr,uid,prod.picking_id.id,context=context)

        #self.pool.get('stock.picking').write( cr, uid, prod.picking_id.id, {'move_lines':[(6,0,lines)]}, context=context)
        #self.pool.get('stock.move').action_cancel(cr,uid, cancel_moves,context)
        #if try_assign:
        #    self.pool.get('stock.picking')._try_assign(cr, uid, production.picking_id, context)


    def _split(self, cr, uid, id, quantity, context):
        """
        Sets the quantity to produce for production with id 'id' to 'quantity' and
        creates a new production order with the deference between current amount and
        the new quantity.
        """

        production = self.browse(cr, uid, id, context)
        if production.state != 'confirmed':
            raise osv.except_osv(_('Error !'), _('Production order "%s" is not in "Waiting Goods" state.') % production.name)
        if quantity >= production.product_qty:
            raise osv.except_osv(_('Error !'), _('Quantity must be greater than production quantity in order "%s" (%s / %s)') % (production.name, quantity, production.product_qty))

        # Create new production, but ensure product_lines is kept empty.
        new_production_id = self.copy(cr, uid, id, {
            'product_lines': [],
            'move_prod_id': False,
            'product_qty': production.product_qty - quantity, 'product_uos_qty' : False, 'product_uos':False 
        }, context)
#Andy        
        old_prod_qty = production.product_qty
#E        
        self.write(cr, uid, production.id, {
            'product_qty': quantity,
            'product_lines': [], 'product_uos_qty' : False, 'product_uos':False 
        }, context)

        self.action_compute(cr, uid, [ new_production_id])
#Andy: UoS maybe "variable", so clear it. update the qty of the stock 2 stock picking.        
        #prod_obj.write(cr, uid, prod.id, {'product_qty' : quantity, 'product_uos_qty' : False, 'product_uos':False })
        org_plan_running = {}
        if production.picking_id:
            move_lines_obj = self.pool.get('stock.move')
            for move_line in  production.picking_id.move_lines:
                line_qty = move_line.product_qty
                move_lines_obj.write(cr, uid, move_line.id, {'product_qty' : quantity * line_qty / old_prod_qty, 'product_uos_qty' : False, 'product_uos':False})
                #If Procurement Order is confirmed state, modify the plan qty else modify the new plan to from stock.
                for procurement in move_line.procurements:
                    if procurement.state in ('draft','confirmed','exception','waiting'):
                        org_plan_running[move_line.product_id.id] = 'DEC' #Draft or Confirmed
                        self.pool.get('procurement.order').write( cr, uid, [procurement.id],{'product_qty' : quantity * line_qty / old_prod_qty, 'product_uos_qty' : False, 'product_uos':False})
                    else:
                        org_plan_running[move_line.product_id.id] = 'RR' #Ready or Running
#E        
        self._change_prod_qty( cr, uid, production.id ,quantity, context)       
        workflow = netsvc.LocalService("workflow")
        workflow.trg_validate(uid, 'mrp.production', new_production_id, 'button_confirm', cr)
        new_production = self.browse(cr, uid, new_production_id, context) 
        if new_production.picking_id: 
            #workflow.trg_write(uid, 'stock.picking', new_production.picking_id.id, cr)
            for move in new_production.picking_id.move_lines:
                if move.procurements:
                    for procurement in move.procurements:
                        if org_plan_running[move.product_id.id] == 'RR':
                            self.pool.get('procurement.order').write( cr, uid, [procurement.id],{'procure_method': 'make_to_stock'})
                        workflow.trg_validate(uid, 'procurement.order', procurement.id, 'button_check', cr)

        return [id, new_production_id]

    def action_confirm(self, cr, uid, ids):
        """ Confirms production order.
        @return: Newly generated picking Id.
        """
        picking_id = False
        proc_ids = []
        seq_obj = self.pool.get('ir.sequence')
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        for production in self.browse(cr, uid, ids):
            if not production.product_lines:
                self.action_compute(cr, uid, [production.id])
                production = self.browse(cr, uid, [production.id])[0]
            routing_loc = None
            pick_type = 'internal'
            address_id = False
            if production.bom_id.routing_id and production.bom_id.routing_id.location_id:
                routing_loc = production.bom_id.routing_id.location_id
                if routing_loc.usage <> 'internal':
                    pick_type = 'out'
                address_id = routing_loc.address_id and routing_loc.address_id.id or False
                routing_loc = routing_loc.id
            pick_name = seq_obj.get(cr, uid, 'stock.picking.' + pick_type)
            picking_id = pick_obj.create(cr, uid, {
                'name': pick_name,
                'origin': (production.origin or '').split(':')[0] + ':' + production.name,
                'type': pick_type,
                'move_type': 'one',
                'state': 'auto',
                'address_id': address_id,
                'auto_picking': self._get_auto_picking(cr, uid, production),
                'company_id': production.company_id.id,
            })
            picking_in_name = seq_obj.get(cr, uid, 'stock.picking.in')
            picking_in_id = pick_obj.create(cr, uid, {
                'name': picking_in_name,
                'origin': (production.origin or '').split(':')[0] + ':' + production.name,
                'type': 'in',
                'move_type': 'one',
                'state': 'auto',
                'address_id': address_id,
                'auto_picking': False, #self._get_auto_picking(cr, uid, production),
                'company_id': production.company_id.id,
            })
            
            source = production.product_id.product_tmpl_id.property_stock_production.id
            data = {
                #'name':'PROD:' + production.name,
                'name': ('%s:[%s]%s') % (production.name,production.product_id.default_code,production.product_id.name),
                'date': production.date_planned,
                'product_id': production.product_id.id,
                'product_qty': production.product_qty,
                'product_uom': production.product_uom.id,
                'product_uos_qty': production.product_uos and production.product_uos_qty or False,
                'product_uos': production.product_uos and production.product_uos.id or False,
                'location_id': source,
                'location_dest_id': production.location_dest_id.id,
                'move_dest_id': production.move_prod_id.id,
                'state': 'waiting',
                'company_id': production.company_id.id,
                'picking_id': picking_in_id,
            }
            res_final_id = move_obj.create(cr, uid, data)
            move_obj.action_confirm(cr, uid, [res_final_id])
            wf_service.trg_validate(uid, 'stock.picking', picking_in_id, 'button_confirm', cr)
            self.write(cr, uid, [production.id], {'picking_in_id': picking_in_id, 'move_created_ids': [(6, 0, [res_final_id])]})
            #Andy modify the chained picking names
            picking_out = pick_obj.browse(cr, uid, picking_id, context=None)
            if pick_name <> picking_out.name:
                pick_obj.write(cr, uid, [picking_id], {'name': pick_name, 'type': pick_type})
            picking_in = pick_obj.browse(cr, uid, picking_in_id, context=None)
            if picking_in_name <> picking_in.name:
                pick_obj.write(cr, uid, [picking_in_id], {'name': picking_in_name, 'type': 'in'})            
            #Andy End
            moves = []
            for line in production.product_lines:
                move_id = False
                newdate = production.date_planned
                if line.product_id.type in ('product', 'consu'):
                    res_dest_id = move_obj.create(cr, uid, {
                        # Felix name -> detail name
                        #'name':'PROD:' + production.name,
                        'name': u"%s: [%s]%s" % (production.name,line.product_id.default_code,line.product_id.name),
                        'date': production.date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'location_id': routing_loc or production.location_src_id.id,
                        'location_dest_id': source,
                        'move_dest_id': res_final_id,
                        'state': 'waiting',
                        'company_id': production.company_id.id,
                    })
                    moves.append(res_dest_id)
                    move_id = move_obj.create(cr, uid, {
                        #'name':'PROD:' + production.name,
                        'name': u"%s: [%s]%s" % (production.name,line.product_id.default_code,line.product_id.name),
                        'picking_id':picking_id,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'date': newdate,
                        'move_dest_id': res_dest_id,
                        'location_id': production.location_src_id.id,
                        'location_dest_id': routing_loc or production.location_src_id.id,
                        'state': 'waiting',
                        'company_id': production.company_id.id,
                    })
                proc_name = (production.origin or '').split(':')[0] + ':' + production.name
                if line.product_id.type in ('service'):
                    proc_name = proc_name + ':' + picking_in_name
                proc_id = proc_obj.create(cr, uid, {
                    'name': proc_name,
                    'origin': proc_name,
                    'date_planned': newdate,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'product_uos_qty': line.product_uos and line.product_qty or False,
                    'product_uos': line.product_uos and line.product_uos.id or False,
                    'location_id': production.location_src_id.id,
                    'procure_method': line.product_id.procure_method,
                    'supply_method': line.product_id.supply_method,
                    'move_id': move_id,
                    'company_id': production.company_id.id,
                })
                wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                proc_ids.append(proc_id)
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            self.write(cr, uid, [production.id], {'picking_id': picking_id, 'move_lines': [(6,0,moves)], 'state':'confirmed'})
            message = _("Manufacturing order '%s' is scheduled for the %s.") % (
                production.name,
                datetime.strptime(production.date_planned,'%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
            )
            self.log(cr, uid, production.id, message)
        return picking_id

    _columns = {
        'picking_in_id': fields.many2one('stock.picking', 'Picking Finished Goods', readonly=True, ondelete="restrict"),
    }

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
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
        wf_service = netsvc.LocalService("workflow")
        final_product_todo = []

        produced_qty = 0
        if production_mode == 'consume_produce':
            produced_qty = production_qty

        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or (produced_product.product_id.id<>production.product_id.id):
                continue
            produced_qty += produced_product.product_qty
        #Andy, 生产已经报完工，但还没有入库，算完成数量,生产数量也计算取得
        production_product_qty = produced_qty - production_qty
        for produce_product in production.move_created_ids:
            if (produce_product.scrapped) or (produce_product.product_id.id<>production.product_id.id):
                continue
            production_product_qty += produce_product.product_qty
            if produce_product.state == 'assigned':
                produced_qty += produce_product.product_qty
        #Andy End

        if production_mode in ['consume','consume_produce']:
            consumed_products = {}
            check = {}
            scrapped = map(lambda x:x.scrapped,production.move_lines2).count(True)

            #计算原材料实际投料数量，不取计划的数量（product_line）
            rw_planned_products = {}
            for rw_product in production.move_lines:
                rw_planned_products[rw_product.product_id.id] = rw_product.product_qty
        
            for rw_product in production.move_lines2:
                if rw_product.scrapped:
                    continue
                if not rw_planned_products.get(rw_product.product_id.id, False):
                    rw_planned_products[rw_product.product_id.id] = rw_product.product_qty
                else:
                    rw_planned_products[rw_product.product_id.id] += rw_product.product_qty

            for f in production.product_lines:
                if not rw_planned_products.get(f.product_id.id, False):
                    rw_planned_products[rw_product.product_id.id] = f.product_qty
            #End
            for consumed_product in production.move_lines2:
                consumed = consumed_product.product_qty
                if consumed_product.scrapped:
                    continue
                if not consumed_products.get(consumed_product.product_id.id, False):
                    consumed_products[consumed_product.product_id.id] = consumed_product.product_qty
                    check[consumed_product.product_id.id] = 0
                for f in production.product_lines:
                    if f.product_id.id == consumed_product.product_id.id:
                        if (len(production.move_lines2) - scrapped) > len(production.product_lines):
                            check[consumed_product.product_id.id] += consumed_product.product_qty
                            consumed = check[consumed_product.product_id.id]
                        rest_consumed = produced_qty * rw_planned_products[f.product_id.id] / production_product_qty - consumed
                        consumed_products[consumed_product.product_id.id] = rest_consumed

            for raw_product in production.move_lines:
                for f in production.product_lines:
                    if f.product_id.id == raw_product.product_id.id:
                        consumed_qty = consumed_products.get(raw_product.product_id.id, 0)
                        if consumed_qty == 0:
                            consumed_qty = production_qty * rw_planned_products[f.product_id.id] / production_product_qty
                        #Andy 如果完工数量>=生产数量直接全部领料
                        if produced_qty >= production_product_qty:
                            consumed_qty = raw_product.product_qty
                        #Andy End
                        if consumed_qty > 0:
                            stock_mov_obj.action_consume(cr, uid, [raw_product.id], consumed_qty, raw_product.location_id.id, context=context)

        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            vals = {'state':'confirmed'}
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
            #Andy: All FG moves are not finished, to check by warehouse user.
            #Andy: So, here should modify. action_consume contain the action_done, but we can not finish the move.
            first_move = 0
            for produce_product in production.move_created_ids:
                if first_move == 0:
                    first_move = produce_product.id
                if first_move > produce_product.id:
                    first_move = produce_product.id
                    
            assign_qty = 0
            for produce_product in production.move_created_ids:
                if produce_product.scrapped:
                    continue
                if first_move < produce_product.id:
                    assign_qty += produce_product.product_qty
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if first_move < produced_product.id:
                    assign_qty += produced_product.product_qty
                
            #produced_qty = produced_products.get(produce_product.product_id.id, 0)
            #rest_qty = production.product_qty - produced_qty
            rest_qty = production_product_qty - assign_qty
            mov_data = stock_mov_obj.browse(cr, uid, [first_move])[0]
            update_val = {}
            if rest_qty <= production_qty:
                production_qty = rest_qty
                #if production_qty > 0:
                #    update_val['product_qty'] = production_qty 
                #    update_val['product_uos_qty'] = update_val['product_qty'] / mov_data.product_qty * mov_data.product_uos_qty
                #    stock_mov_obj.write(cr, uid, [first_move], update_val)
                #else:
                #stock_mov_obj.action_consume(cr, uid, [first_move], production_qty, context=context)
                stock_mov_obj.force_assign(cr, uid, [first_move], context)  #Andy
                wf_service.trg_write(uid, 'stock.picking', production.picking_in_id.id, cr)
            else :
                stock_mov_obj.action_split(cr, uid, [first_move], production_qty, split_by_qty=production_qty, with_lot=mov_data.product_id.track_production or False, context=context)
                update_val['product_qty'] = mov_data.product_qty - production_qty 
                update_val['product_uos_qty'] = update_val['product_qty'] / mov_data.product_qty * mov_data.product_uos_qty  
                update_val['state'] = 'confirmed'                  
                #update_val['prodlot_id'] = mov_data.prodlot_id and mov_data.prodlot_id.id or False
                stock_mov_obj.write(cr, uid, [first_move], update_val)

        #End Modify by Andy

        for raw_product in production.move_lines2:
            new_parent_ids = []
            parent_move_ids = [x.id for x in raw_product.move_history_ids]
            for final_product in production.move_created_ids2:
                if final_product.id not in parent_move_ids:
                    new_parent_ids.append(final_product.id)
            for new_parent_id in new_parent_ids:
                stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})

        #Andy 不报完工
        #if production_mode == 'consume_produce':            
        #    wf_service = netsvc.LocalService("workflow")
        #    wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce_done', cr)
        return True  

    def test_production_done(self, cr, uid, ids):
        """ Tests whether production is done or not.
        @return: True or False
        """
        return False

    def _get_auto_picking(self, cr, uid, production):
        return False

    def test_production_ready(self, cr, uid, ids):
        finish = False
        for production in self.browse(cr, uid, ids):
            if production.picking_id:
                if production.picking_id.state == 'done' or production.picking_id.backorder_id:
                    finish = True
                    break
                if production.picking_id.move_lines:
                    for move in production.picking_id.move_lines:
                        if move.state in ('assigned','done'):
                            finish = True
                            break
            else:
                finish = True

        return finish

    def action_in_production(self, cr, uid, ids):
        """ Changes state to In Production and writes starting date.
        @return: True
        """
        if not super(mrp_production, self).action_in_production(cr, uid, ids):
            return False
        move_obj = self.pool.get('stock.move')
        for production in self.browse(cr, uid, ids):
            if production.picking_id and production.picking_id.move_lines:
                for move in production.picking_id.move_lines:
                    if not move.move_dest_id:
                        continue                        
                    cr.execute('select sum(product_qty) from stock_move where origin=%s and product_id = %s', (move.origin or '',move.product_id.id))
                    product_qty = cr.fetchone()[0]
                    move_obj.write(cr, uid, [move.move_dest_id.id], {'product_qty': product_qty})
        return True

    def test_picking_exception(self, cr, uid, ids):
        finish = False
        for production in self.browse(cr, uid, ids):
            if production.picking_id:
                if production.picking_id.state == 'cancel':
                    finish = True
                    break
        return finish    

    def action_ready(self, cr, uid, ids):
        """ Changes the production state to Ready and location id of stock move.
        @return: True
        """
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'ready'})

        for (production_id,name) in self.name_get(cr, uid, ids):
            production = self.browse(cr, uid, production_id)
            if production.move_prod_id:
                #ApeX company problem: Chained DN Move finished, but not start MO yet sometimes.
                if production.move_prod_id.state == 'done':
                    continue
                move_obj.write(cr, uid, [production.move_prod_id.id],
                        {'location_id': production.location_dest_id.id})

            message = _("Manufacturing order '%s' is ready to produce.") % ( name,)
            self.log(cr, uid, production_id, message)
        return True  
mrp_production()

class StockPicking(osv.osv):
    _inherit = "stock.picking"
 
    def test_finished(self, cr, uid, ids):
        wf_service = netsvc.LocalService("workflow")
        res = super(StockPicking, self).test_finished(cr, uid, ids)
        production_obj = self.pool.get('mrp.production')
        #
        for picking in self.browse(cr, uid, ids):
            finish = True
            check = False
            for move in picking.move_lines:
                if res and move.production_id:
                    check = True                    
                    finish = finish and move.state == 'done'
            if check and finish:
                production_do = production_obj.browse(cr, uid, [move.production_id.id])[0]
                for move_prod in production_do.move_created_ids:                                        
                    finish = finish and move_prod.state == 'done'
                if finish:
                    res = production_obj.action_production_end( cr, uid, [production_do.id])
                    #Andy: The move of new Procurement Order created manually is finished, but Procuremnt Order is not finished auto.
                    if res and production_do and production_do.move_prod_id and not production_do.move_prod_id.picking_id:                    
                        for procurement in production_do.move_prod_id.procurements:
                            self.pool.get('procurement.order').action_done( cr, uid, [procurement.id])
        return res

    def action_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        move_obj = self.pool.get('stock.move')
        for pick in self.browse(cr, uid, ids):
            #move_ids = [x.id for x in pick.move_lines if x.state == 'confirmed'] Andy
            move_ids = [x.id for x in pick.move_lines if x.state in ('confirmed','waiting')]            
            move_a_ids = [x.id for x in pick.move_lines if x.state in ('assigned')]
            if not move_ids and not move_a_ids:
                raise osv.except_osv(_('Warning !'),_('Not enough stock, unable to reserve the products.'))
            if move_ids:
                move_obj.action_assign(cr, uid, move_ids)
            elif move_a_ids:
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
        return True

    def test_assigned(self, cr, uid, ids):
        """ Tests whether the move is in assigned state or not.
        @return: True or False
        """
        ok = super(StockPicking, self).test_assigned(cr, uid, ids)
        if ok:            
            production_obj = self.pool.get('mrp.production')
            pick_ids = self.search(cr, uid, [('backorder_id', 'in', ids)])
            if not pick_ids:
                pick_ids = ids
            prod_ids = production_obj.search(cr, uid, [('picking_id', 'in', pick_ids)])
            for production in production_obj.browse(cr, uid, prod_ids, context={}):
                if production.state in ('confirmed'):
                    production_obj.action_ready(cr, uid, [production.id])
        return ok
    
    def test_done(self, cr, uid, ids, context=None):
        """ Test whether the move lines are done or not.
        @return: True or False
        """
        ok = False
        production_obj = self.pool.get('mrp.production')
        for pick in self.browse(cr, uid, ids, context=context):
            prod_ids = production_obj.search(cr, uid, [('picking_id', '=', pick.id)])
            if prod_ids and pick.backorder_id and pick.backorder_id.state=='done':
                ok = False #True
        if not ok:
            super(StockPicking, self).test_done(cr, uid, ids)
        return ok
StockPicking()

class PurchaseOrder(osv.osv):
    _inherit = "purchase.order"
    
    def action_picking_create(self,cr, uid, ids, *args):
        picking_id = False
        for order in self.browse(cr, uid, ids):
            loc_id = order.partner_id.property_stock_supplier.id
            istate = 'none'
            if order.invoice_method=='picking':
                istate = '2binvoiced'
            pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                'name': pick_name,
                'origin': order.name+((order.origin and (':'+order.origin)) or ''),
                'type': 'in',
                'address_id': order.dest_address_id.id or order.partner_address_id.id,
                'invoice_state': istate,
                'purchase_id': order.id,
                'company_id': order.company_id.id,
                'move_lines' : [],
            })
            todo_moves = []
            for order_line in order.order_line:
                if not order_line.product_id:
                    continue
                if order_line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    dest = order.location_id.id
                    move = self.pool.get('stock.move').create(cr, uid, {
                        'name': order.name + ': ' +(order_line.name or ''),
                        'product_id': order_line.product_id.id,
                        'product_qty': order_line.product_qty,
                        'product_uos_qty': order_line.product_qty,
                        'product_uom': order_line.product_uom.id,
                        'product_uos': order_line.product_uom.id,
                        'date': order_line.date_planned,
                        'date_expected': order_line.date_planned,
                        'location_id': loc_id,
                        'location_dest_id': dest,
                        'picking_id': picking_id,
                        #'move_dest_id': order_line.move_dest_id.id, #Andy remove this link between moves, for the link changed.
                        'state': 'draft',
                        'purchase_line_id': order_line.id,
                        'company_id': order.company_id.id,
                        'price_unit': order_line.price_unit
                    })
                    #if order_line.move_dest_id: #Andy remove this link between moves, for the link changed.
                    #    self.pool.get('stock.move').write(cr, uid, [order_line.move_dest_id.id], {'location_id':order.location_id.id})
                    todo_moves.append(move)
            self.pool.get('stock.move').action_confirm(cr, uid, todo_moves)
            self.pool.get('stock.move').force_assign(cr, uid, todo_moves)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return picking_id

PurchaseOrder()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
