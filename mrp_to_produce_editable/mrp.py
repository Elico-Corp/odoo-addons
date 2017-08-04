# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields
from openerp import netsvc
from openerp.addons.product import _common
from openerp.tools import float_compare
from openerp.tools.translate import _


class mrp_production(orm.Model):
    _inherit = 'mrp.production'
    #here we make the "products to produce" editable in state:
        # confirmed, ready.
    _columns = {
        'date_start': fields.datetime(
            'Start Date',
            select=True,
            states={'done': [('readonly', '=', True)]}),
        'date_finished': fields.datetime(
            'End Date',
            select=True,
            states={'done': [('readonly', '=', True)]}),
        'move_created_ids': fields.one2many(
            'stock.move',
            'production_id',
            'Products to Produce',
            domain=[('state', 'not in', ('done', 'cancel'))],
            readonly=True,
            states={
                'draft': [('readonly', False)],
                'confirmed': [('readonly', False)],
                'ready': [('readonly', False)],
            }),

        'picking_finished_id': fields.many2one(
            'stock.picking', 'Picking Finished Goods',
            readonly=True, ondelete="restrict"),
        # should be only readonly in done state. Alex
        'date_planned': fields.datetime(
            'Scheduled Date',
            required=True,
            select=1,
            states={'done': [('readonly', True)]}),
        'origin': fields.char(
            'Source Document',
            size=64,
            states={'done': [('readonly', True)]},
            help="Reference of the document that "
            "generated this production order request."),
    }

    _defaults = {
        'user_id': lambda self, cr, uid, c: False
    }

    def force_production(self, cr, uid, ids, *args):
        """ Assigns products.
        @param *args: Arguments
        @return: True
        """
        super(mrp_production, self).force_production(
            cr, uid, ids, args)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_write(uid, 'mrp.production', ids[0], cr)
        wf_service.trg_write(
            uid, 'stock.picking',
            [prod.picking_id.id for prod in self.browse(cr, uid, ids)][0], cr)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['picking_finished_id'] = False
        default['date_start'] = False
        default['date_finished'] = False
        return super(mrp_production, self).copy(
            cr, uid, id,
            default, context=context)

    def _make_production_finished_shipment(self, cr, uid, production, context=None):
        ir_sequence = self.pool.get('ir.sequence')
        stock_picking = self.pool.get('stock.picking')
        pick_type = 'in'

        # Take next Sequence number of shipment base on type
        if pick_type != 'internal':
            pick_name = ir_sequence.get(cr, uid, 'stock.picking.' + pick_type)
        else:
            pick_name = ir_sequence.get(cr, uid, 'stock.picking')

        picking_id = stock_picking.create(cr, uid, {
            'name': pick_name,
            'origin': (production.origin or '').split(':')[0] + ':' + production.name,
            'type': pick_type,
            'move_type': 'direct',
            'state': 'assigned',
            'auto_picking': self._get_auto_picking(cr, uid, production),
            'company_id': production.company_id.id,
        })
        production.write({'picking_finished_id': picking_id}, context=context)
        return picking_id

    def _make_production_produce_line(
            self, cr, uid, production, context=None):
        '''
        Here we inherit this method to create an extra picking
        of finished product'''
        # add the stock picking for mrp production.
        wf_service = netsvc.LocalService('workflow')
        picking_finished_id = production.picking_finished_id.id
        if not picking_finished_id:
            picking_finished_id = self._make_production_finished_shipment(
                cr, uid, production, context=context)
            production.write({
                'picking_finished_id': picking_finished_id
            })

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
        }

        data['picking_id'] = picking_finished_id
        move_id = stock_move.create(cr, uid, data, context=context)
        production.write(
            {'move_created_ids': [(6, 0, [move_id])]}, context=context)

        # trigger confirm
        wf_service.trg_validate(
            uid, 'stock.picking', picking_finished_id,
            'button_confirm', cr)
        return move_id

    def action_produce(
        self, cr, uid,
            production_id, production_qty, production_mode, context=None):
        """ To produce final product based on production mode
        (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials
        will be done/consumed.
        If Production mode is consume & produce, all stock move lines of
        raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce
        @param production_mode: specify production mode
        (consume/consume&produce).
        @return: True

        << rewrite all of this to cancel the except_osv that Warning
            no enough material.
        << recalculate the qty of raw products.
        """
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)

        wf_service = netsvc.LocalService("workflow")
        if not production.move_lines and production.state == 'ready':
            # trigger workflow if not products to consume (eg: services)
            wf_service.trg_validate(
                uid, 'mrp.production', production_id, 'button_produce', cr)

        produced_qty = 0
        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or \
                    produced_product.state in (
                        'cancel', 'draft', 'waiting') or\
                    (produced_product.product_id.id !=
                        production.product_id.id):
                continue
            produced_qty += produced_product.product_qty

        # <<<<< change begins we also calculate the qty of unproduced product
        unproduced_qty = 0
        for unproduced_product in production.move_created_ids:
            if (unproduced_product.scrapped) or \
                    (unproduced_product.product_id.id !=
                        production.product_id.id):
                continue
            if unproduced_product.state in ('assigned', 'done'):
                produced_qty += unproduced_product.product_qty
            elif unproduced_product.state in ('draft', 'waiting', 'confirmed'):
                unproduced_qty += unproduced_product.product_qty
        # <<<<< change ends
        if production_mode in ['consume', 'consume_produce']:
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
                total_consume = (
                    (production_qty + produced_qty) * scheduled.product_qty / production.product_qty)

                # qty available for consume and produce
                qty_avail = scheduled.product_qty - consumed_data.get(scheduled.product_id.id, 0.0)

                if float_compare(qty_avail, 0, precision_rounding=scheduled.product_id.uom_id.rounding) <= 0:
                    # there will be nothing to consume for this raw material
                    continue

                raw_product = [move for move in production.move_lines if move.product_id.id==scheduled.product_id.id]
                if raw_product:
                    # qtys we have to consume
                    # <<< change begins here we change the official way to calculate the qty
                    # TODO try to do the rounding because this may cause the stock number wrong.
                    qty = (production_qty / (produced_qty + unproduced_qty)) * scheduled.product_qty
                    # <<< change ends.

                    if float_compare(qty, 0, precision_rounding=scheduled.product_id.uom_id.rounding) <= 0:                        
                        # we already have more qtys consumed than we need
                        continue
                    # here we consume raw products.
                    raw_product[0].action_consume(qty, raw_product[0].location_id.id, context=context)

        if production_mode == 'consume_produce':
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty

            for produce_product in production.move_created_ids:
                produced_qty2 = produced_products.get(produce_product.product_id.id, 0)
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                # change begins here: the totoal qty of to produce products changed.
                rest_qty = (subproduct_factor * (unproduced_qty + produced_qty)) - produced_qty
                # change ends here.
                if rest_qty > 0 and produce_product.state in ('draft', 'waiting'):
                    # here we consume product.
                    stock_mov_obj.action_consume(cr, uid, [produce_product.id], (subproduct_factor * production_qty), context=context)

        for raw_product in production.move_lines2:
            new_parent_ids = []
            parent_move_ids = [x.id for x in raw_product.move_history_ids]
            for final_product in production.move_created_ids2:
                if final_product.id not in parent_move_ids:
                    new_parent_ids.append(final_product.id)
            for new_parent_id in new_parent_ids:
                stock_mov_obj.write(
                    cr, uid,
                    [raw_product.id],
                    {'move_history_ids': [(4, new_parent_id)]})

        wf_service.trg_validate(
            uid, 'mrp.production', production_id, 'button_produce_done', cr)
        return True

    def check_produce_done(self, cr, uid, ids, context=None):
        if not ids:
            return
        ids = ids and ids[0]
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(
            uid, 'mrp.production',
            ids,
            'button_produce_done', cr)


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def action_done(self, cr, uid, ids, context=None):
        super(stock_picking, self).action_done(
            cr, uid, ids, context=context)
        # trigger the mrp production order.
        # get the production_id
        if ids:
            if isinstance(ids, (int, long)):
                ids = [ids]
            mrp_obj = self.pool.get('mrp.production')
            wf_service = netsvc.LocalService('workflow')
            mo_ids = mrp_obj.search(
                cr, uid,
                ['|', ('picking_id', 'in', ids), ('picking_finished_id', 'in', ids)],
                context=context)
            if mo_ids:
                wf_service.trg_validate(
                    uid, 'mrp.production',
                    mo_ids[0],
                    'button_produce_done', cr)


class product_product(orm.Model):
    _inherit = 'product.product'
    _defaults = {
        'auto_pick': False
    }
