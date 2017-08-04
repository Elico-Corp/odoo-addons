# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import logging
import time


from openerp.osv import orm, fields, osv
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round

from openerp.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)


class stock_duty_zone(orm.Model):
    _name = 'stock.duty.zone'

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'price_type_id': fields.many2one(
            'product.price.type', 'Product cost field',
            required=True,
            help="Please input the price type associated to this duty zone"),
        'val_account_id': fields.many2one(
            'account.account',
            "Stock valuation account",
            required=True,
            domain=[('type', 'not in', ('view', 'closed'))]),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'location_ids': fields.one2many(
            'stock.location', 'duty_zone_id', 'Locations')
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid, c).company_id.id
    }

    def if_support_zone(self, cr, uid, context=None):
        '''check if the current company support duty zone or not'''
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id
        return company_id.support_duty_zone

    def _check_one_price_type_one_zone(self, cr, uid, ids, context=None):
        '''make sure one cost price (eg. duty free cost, duty paid cost), one duty zone.

        ----
        The price type should also be unique per (company, price)
        '''
        for zone in self.browse(cr, uid, ids, context=context):
            zone_ids = False
            price_type = zone.price_type_id
            zone_ids = self.search(cr, uid, [('price_type_id', '=', price_type.id)], context)
            if len(zone_ids) > 1:
                return False
        return True

    _constraints = [
        (_check_one_price_type_one_zone,
            'Error!\nYou cannot assign the same price type to more than two duty zones!', [])
    ]


class product_price_type(osv.osv):
    _inherit = 'product.price.type'

    _sql_constraints = [
        ('field_unique', 'unique(company_id, field)', 'There is already price type for this price exists!')
    ]


class stock_location(orm.Model):
    _inherit = 'stock.location'

    _columns = {
        'duty_zone_id': fields.many2one(
            'stock.duty.zone', 'Duty Zone')
    }

    def button_delete_location(self, cr, uid, ids, context=None):
        '''This is for a triky button to unlink the one2many field with delete
        the record in database.'''

        duty_zone_id = False
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        for loc in self.browse(cr, uid, ids, context=context):
            duty_zone_id = loc.duty_zone_id and loc.duty_zone_id.id or False
            loc.write({'duty_zone_id': False})
        return {
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'stock.duty.zone',
            'view_id': False,
            'res_id': duty_zone_id,
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    def _check_parent_location_child_location_one_zone(self, cr, uid, ids, context=None):
        '''Make sure zone of the parent location is the same as the child loation.
        otherwise, the available quanitty of products in a duty zone would not be right.'''
        for location in self.browse(cr, uid, ids, context=context):
            parent = location.location_id
            if parent and parent.duty_zone_id:
                if parent.duty_zone_id.id != location.duty_zone_id.id:
                    return False
        return True

    _constraints = [
        (_check_parent_location_child_location_one_zone,
            'Error!\nYou cannot assign the child location a zone '
            'different with the parent location\'s!', [])
    ]


class res_company(orm.Model):
    _inherit = 'res.company'
    _columns = {
        'support_duty_zone': fields.boolean('Support duty zones')
    }

    _defaults = {
        'support_duty_zone': False
    }


class stock_move(orm.Model):
    _inherit = 'stock.move'
    # TODO refact the structures.
    # currently just mainly reference from module: purchase_landed_costs
    def copy_data(self, cr, uid, id, default=None, context=None):
	res = super(stock_move, self).copy_data(cr, uid, id, default, context)
	if 'duty_rule_computed' in res:
	    res.update({'duty_rule_computed': False})
	return res

    def copy(self, cr, uid, id, default=None, context=None):
        '''rewrite the copy method to avoid copy the field: landed_cost_line_ids'''
        default = default or {}
        default.update({'landed_cost_line_ids': [], 'duty_rule_computed': False})
        return super(stock_move, self).copy(
            cr, uid, id, default, context=context)

    def _landing_cost(self, cr, uid, ids, name, args, context=None):
        '''Get the landing costs for the move line'''
        if not ids:
            return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs = 0.0
            for costs in line.landed_cost_line_ids or ():
                # based on product value
                if (costs.distribution_type_id.landed_cost_type == 'value' and
                        costs.distribution_type_id.apply_on == 'line'):
                    landed_costs += costs.amount
                # based on product volume
                elif (costs.distribution_type_id.landed_cost_type == 'volume' and
                        costs.distribution_type_id.apply_on == 'line'):
                    landed_costs += line.line_volume * costs.amount
                # based on product qty
                else:
                    landed_costs += costs.amount * line.product_qty
            result[line.id] = landed_costs
        return result

    def _line_volume(self, cr, uid, ids, name, args, context=None):
        '''The total volume of the move line'''
        if not ids:
            return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            volume_factor = line.product_uom and line.product_uom.volume_factor or 1.0
            res[line.id] = volume_factor * line.product_qty
        return res

    def _landing_costs_order(self, cr, uid, ids, name, args, context=None):
        '''Get the landing cost from the order.
        If the landed costs is from purchase order and distributed by value, for all the LC
            we use the purchse price from purchase order.
        If the landed costs is not from purchase order, we use the standard_price of product.

        [Refactory Note]: the field name of order in the line level may be different.
            eg. for stock move, the field is : picking_id; for purchase order: order_id
            can use getattr and may change the function params.
        '''
        if not ids:
            return {}
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        # stock moves
        for line in lines:
            landed_costs = 0.0
            order = line.picking_id
            if order:
                tot_value = 0.0
                for l in order.move_lines:
                    tot_value += l.product_id.standard_price * l.product_qty
                # distribution of landed costs of Picking
                if not order.landed_cost_line_ids:
                    result[line.id] = landed_costs

                # Base value (value from purchase order)
                # TOFIX: check constraint #1: after the Incoming shipment is created,
                #           if the stock move is manually added, the distribution of value LC
                #           would not be right because there is no purchase order line accordingly.
                # TODO refactory note: extract the get value method.
                if order.landed_cost_base_value and order.purchase_id:
                    try:
                        # use the price with taxes
                        if line.purchase_line_id:
                            landed_costs += (order.landed_cost_base_value * line.purchase_line_subtotal /
                                             order.purchase_id.amount_untaxed)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError! computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s. (The total value of the stock picking might be zero.)' % (line.name, line.picking_id.name))
                
                # Base value (cost of product)
                elif order.landed_cost_base_value and not order.purchase_id:
                    try:
                        landed_costs += (order.landed_cost_base_value * line.product_id.standard_price *
                                         line.product_qty / tot_value)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError! computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s. (The total value of the stock picking might be zero.)' % (line.name, line.picking_id.name))
                # Base quantity (base on purchase order if we have purchse order)
                if order.landed_cost_base_quantity and order.purchase_id:
                    try:
                        if line.purchase_line_id:
                            landed_costs += (order.landed_cost_base_quantity /
                                             order.purchase_id.quantity_total *
                                             line.purchase_line_id.product_qty)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError, computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s' % (line.name, line.picking_id.name))
                # Base quantity (base on stock picking)
                elif order.landed_cost_base_quantity and not order.purchase_id:
                    try:
                        landed_costs += (order.landed_cost_base_quantity /
                                         order.quantity_total *
                                         line.product_qty)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError, computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s' % (line.name, line.picking_id.name))
                # Base Volume (base on purchase order)
                if order.landed_cost_base_volume and order.purchase_id:
                    try:
                        if line.purchase_line_id:
                            landed_costs += (order.landed_cost_base_volume /
                                             order.purchase_id.volume_total *
                                             line.purchase_line_id.line_volume)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError, computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s' % (line.name, line.picking_id.name))
                # Base Volume (base on stock picking)
                elif order.landed_cost_base_volume and not order.purchase_id:
                    try:
                        landed_costs += (order.landed_cost_base_volume /
                                         order.volume_total *
                                         line.line_volume)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError, computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s' % (line.name, line.picking_id.name))
            result[line.id] = landed_costs
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        '''Sum of the landing costs(from line and order)'''
        if not ids:
            return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs = 0.0
            landed_costs += (line.landing_costs + line.landing_costs_order)
            result[line.id] = landed_costs
        return result

    _columns = {
        'line_volume': fields.function(
            _line_volume,
            string="Product CBM"),
        'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'move_id',
            'Landed Costs Positions',),
        'landing_costs': fields.function(
            _landing_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landing Costs'),
        'landing_costs_order': fields.function(
            _landing_costs_order,
            digits_compute=dp.get_precision('Account'),
            string='Landing Costs from Order'),
        'landed_costs': fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs'),
        'purchase_line_subtotal': fields.float(
            'Subtotal', digits_compute=dp.get_precision('Account'),
            help="Used for distribution of landing costs."),
        'duty_rule_computed': fields.boolean('Duty Rule Computed'),
    }

    _defaults = {
        'duty_rule_computed': False
    }

    #
    # here starts the update of average price
    #
    # FIXME: needs refactoring, this code is partially duplicated in stock_picking.do_partial()!
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s'%(move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s.') % (move.id)
            product_qty = partial_data.get('product_qty',0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom',False)
            product_price = partial_data.get('product_price',0.0)
            product_currency = partial_data.get('product_currency',False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            pick = move.picking_id
            location_obj = self.pool.get('stock.location')
            if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                product = move.product_id
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                # get the qty of available Alex (from module: purchase_landed_cost_extended)
                #
                # re-implemented this method, add a new param: domain
                # Note: if extract this module, the function need to be in the new module.
                #
                product_qty_available = location_obj.get_product_qty_of_checked_locations(
                    cr, uid, [],
                    move.product_id.id, domain=[], context=context, states=['done']).get(
                    move.product_id.id, 0.0)

                if qty > 0:
                    new_price = currency_obj.compute(cr, uid, product_currency,
                            move_currency_id, product_price)
                    new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                            product.uom_id.id)
                    if product_qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the standard price
                        amount_unit = product.price_get('standard_price', context=context)[product.id]
                        new_std_price = ((amount_unit * product_qty_available)\
                            + (new_price * qty))/(product_qty_available + qty)
                    # Write the field according to price type field
                    product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(
                        cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency})
                #
                # for the new cost price computation incoming)
                #
                if move.company_id.support_duty_zone:
                    dest_zone = move.location_dest_id.duty_zone_id
                    price_name = dest_zone.price_type_id.field
                    product_qty_available = 0
                    product_qty_available = location_obj.get_product_qty_of_checked_locations(
                        cr, uid, [],
                        move.product_id.id, domain=[('duty_zone_id', '=', dest_zone.id)],
                        context=context, states=['done']).get(
                        move.product_id.id, 0.0)

                    if qty > 0 and dest_zone:
                        # update the transit cost price. PP + landed cost (stock move)
                        if move.purchase_line_id:
                            # move.price_unit purchase price on purchase order.
                            new_price = (move.price_unit * qty + move.landed_costs) / qty
                            # convert the price to the
                            new_price = currency_obj.compute(cr, uid, product_currency,
                                    move_currency_id, product_price)
                            new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                            if product_qty_available <= 0:
                                new_std_price = new_price
                            else:
                                amount_unit = product.price_get(price_name, context=context)[product.id]
                                new_std_price = ((amount_unit * product_qty_available)
                                    + (new_price * qty)) / (product_qty_available + qty)
                            # Write the field according to price type field
                            product_obj.write(cr, uid, [product.id], {price_name: new_std_price})
                        else:
                            # FIXME in this case is: manually created incoming shipment.
                            _logger.debug('When calculating average price, There is no '
                                          'purchase order line in the '
                                          'stock move %s, %d' % (move.name, move.id))
            # case: internal move with LC (update standard cost price and duty zone cost price)
            # If with LC, we update the standard cost price as well.
            #
            elif (pick.type == 'internal') and (move.product_id.cost_method == 'average') and \
                    pick.landed_cost:
                product = move.product_id
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                # update standard cost price
                product_qty_available = 0
                product_qty_available = location_obj.get_product_qty_of_checked_locations(
                    cr, uid, [],
                    move.product_id.id, domain=[],
                    context=context, states=['done']).get(
                    move.product_id.id, 0.0)
                if qty > 0:
                    product_price = (move.product_id.standard_price * qty + move.landed_costs) / qty
                    new_price = currency_obj.compute(
                        cr, uid, product_currency,
                        move_currency_id, product_price)
                    new_price = uom_obj._compute_price(
                        cr, uid, product_uom, new_price,
                        product.uom_id.id)
                    if product_qty_available <= 0:
                        new_std_price = new_price
                    else:
                        amount_unit = product.price_get('standard_price', context=context)[product.id]
                        # if it is internal move, The total quantity doesn't change.
                        new_std_price = ((amount_unit * product_qty_available + move.landed_costs)
                                         / product_qty_available)
                    # Write the field according to price type field
                    product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                # update the new cost prices
                if move.company_id.support_duty_zone:
                    dest_zone = move.location_dest_id.duty_zone_id
                    src_zone = move.location_id.duty_zone_id
                    price_dest_name = dest_zone.price_type_id.field
                    price_src_name = src_zone.price_type_id.field
                    product_qty_available = location_obj.get_product_qty_of_checked_locations(
                        cr, uid, [],
                        move.product_id.id, domain=[('duty_zone_id', '=', dest_zone.id)],
                        context=context, states=['done']).get(
                        move.product_id.id, 0.0)

                    if qty > 0:
                        # get the new price: AP + landed cost
                        # TODO check conversion of currency and uom is right
                        product_price = (getattr(move.product_id, price_src_name) * qty + move.landed_costs) / qty
                        new_price = currency_obj.compute(
                            cr, uid, product_currency,
                            move_currency_id, product_price)
                        new_price = uom_obj._compute_price(
                            cr, uid, product_uom, new_price,
                            product.uom_id.id)
                        if product_qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the old cost price on the dest duty zone.
                            amount_unit = product.price_get(price_dest_name, context=context)[product.id]
                            if self.check_if_cross_zone(pick):
                                new_std_price = ((amount_unit * product_qty_available)
                                                 + (new_price * qty)) / (product_qty_available + qty)
                            # if it is the same zone, The total quantity doesn't change.
                            else:
                                new_std_price = ((amount_unit * product_qty_available + move.landed_costs)
                                                 / (product_qty_available))
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {price_dest_name: new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        self.write(
                            cr, uid, [move.id],
                            {'price_unit': product_price,
                             'price_currency_id': product_currency})
            # case: if we don't have the landed cost but it's cross zone move.
            # no need to update standard cost price, update the dest zone cost price.
            elif (pick.type == 'internal') and (move.product_id.cost_method == 'average') and \
                    move.company_id.support_duty_zone and self.check_if_cross_zone(move):
                dest_zone = move.location_dest_id.duty_zone_id
                src_zone = move.location_id.duty_zone_id
                price_dest_name = dest_zone.price_type_id.field
                price_src_name = src_zone.price_type_id.field
                product = move.product_id

                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                product_qty_available = location_obj.get_product_qty_of_checked_locations(
                    cr, uid, [],
                    move.product_id.id, domain=[('duty_zone_id', '=', dest_zone.id)],
                    context=context, states=['done']).get(
                    move.product_id.id, 0.0)

                if qty > 0:
                    # get the new price: AP of src zone + landed cost
                    # TODO check conversion of currency and uom is right
                    product_price = (getattr(move.product_id, price_src_name) * qty + move.landed_costs) / qty
                    new_price = currency_obj.compute(
                        cr, uid, product_currency,
                        move_currency_id, product_price)
                    new_price = uom_obj._compute_price(
                        cr, uid, product_uom, new_price,
                        product.uom_id.id)
                    if product_qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the old cost price on the dest duty zone.
                        amount_unit = product.price_get(price_dest_name, context=context)[product.id]
                        if self.check_if_cross_zone(pick):
                            new_std_price = ((amount_unit * product_qty_available)
                                             + (new_price * qty)) / (product_qty_available + qty)
                        # if it is the same zone, The total quantity doesn't change.
                        else:
                            new_std_price = ((amount_unit * product_qty_available + move.landed_costs)
                                             / (product_qty_available))
                    # Write the field according to price type field
                    product_obj.write(cr, uid, [product.id], {price_dest_name: new_std_price})

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(
                        cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency})

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty,
                            'picking_id' : move.picking_id.id,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty - product_qty,
                        'product_uos_qty': move.product_qty - product_qty,
                        'prodlot_id': False,
                        'tracking_id': False,
                    })
            #
            # pass all the simple value type of LC to back order move
            #
            self.LC_copy_backorder(cr, uid, move, new_move, context=context)

        for move in too_many:
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                    })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id],{'prodlot_id': prodlot_ids.get(move.id)})
            self.action_done(cr, uid, [move.id], context=context)
            if  move.picking_id.id :
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                            ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [move.id for move in complete]
    #
    # here starts the creation of the account entries
    #

    def _get_reference_accounting_values_for_valuation(self, cr, uid, move, type='', context=None):
        """
        Return the reference amount and reference currency representing the inventory valuation for this move.
        These reference values should possibly be converted before being posted in Journals to adapt to the primary
        and secondary currencies of the relevant accounts.

        :param type: incoming or outgoing, type of the stock moves

        :return the reference currency and amount in that currency
        rewrite this function to get the right cost price.
        """
        product_uom_obj = self.pool.get('product.uom')
	reference_amount = 0.0
        reference_currency_id = False

        # by default the reference currency is that of the move's company
        reference_currency_id = move.company_id.currency_id.id

        default_uom = move.product_id.uom_id.id
        qty = product_uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, default_uom)

        if context is None:
            context = {}
        currency_ctx = dict(context, currency_id=move.company_id.currency_id.id)

        #
        # get the price unit exclude taxes
        #
        price_unit_exclude = None
        if move.purchase_line_id:
            # TO FIX may be rounding issue here.
            price_unit_exclude = move.purchase_line_id.price_subtotal / \
                move.purchase_line_id.product_qty

        # if product is set to average price and a specific value was entered in the picking wizard,
        # we use it [this is standard openerp]
        if move.product_id.cost_method == 'average' and \
                move.price_unit and not move.company_id.support_duty_zone and price_unit_exclude is not None:
            reference_amount = qty * price_unit_exclude
            reference_currency_id = move.price_currency_id.id or reference_currency_id

        # Otherwise we default to the company's valuation price type, considering that the values of the
        # valuation field are expressed in the default currency of the move's company.
        elif not move.company_id.support_duty_zone:
            if context is None:
                context = {}
            currency_ctx = dict(context, currency_id=move.company_id.currency_id.id)
            amount_unit = move.product_id.price_get('standard_price', context=currency_ctx)[move.product_id.id]
            reference_amount = amount_unit * qty
        #
        # for company which supports duty zone we have different way to get the reference amount.
        # here we get the source location of the stock move to get the right cost price.
        if move.company_id.support_duty_zone and move.location_id.usage == 'internal' and \
                type == 'outgoing':
            assert move.location_id.duty_zone_id, 'You '
            'should set the duty zone for location:%s' % move.location_id.complete_name
            price_name = move.location_id.duty_zone_id.price_type_id.field
            amount_unit = move.product_id.price_get(
                price_name, context=currency_ctx)[move.product_id.id]
            reference_amount = amount_unit * qty
        
        # one case is inventory gain.
        elif move.company_id.support_duty_zone and move.location_dest_id.usage == 'internal' and \
                type == 'incoming':
            amount_unit = None
            if move.purchase_line_id:
                # the price (LC and tax not included).
                reference_amount = price_unit_exclude * move.product_qty
                reference_currency_id = move.price_currency_id.id or reference_currency_id
            else:
                assert move.location_dest_id.duty_zone_id, 'You '
                'should set the duty zone for location:%s' % move.location_dest_id.complete_name
                price_name = move.location_dest_id.duty_zone_id.price_type_id.field
                amount_unit = move.product_id.price_get(price_name, context=currency_ctx)[move.product_id.id]
                if amount_unit is None:
                    amount_unit = move.product_id.price_get(
                        'standard_price', context=currency_ctx)[move.product_id.id]
                reference_amount = amount_unit * qty
        return reference_amount, reference_currency_id

    def _get_accounts_duty_zone_valuation(self, cr, uid, move, type='', context=None):
        '''Get accounting data: stock input/output/valuation account.
        For the stock valuation account, we get first from duty zone, if failed,
            get from product category.
        :param move: current stock move
        :param type: incoming or outgoing
        :return journal, journal_id, acc_src, acc_dest, acc_valuation'''

        product_obj = self.pool.get('product.product')
        dest_zone = move.location_dest_id.duty_zone_id
        src_zone = move.location_id.duty_zone_id
        accounts = product_obj.get_product_accounts(cr, uid, move.product_id.id, context)
        if move.location_id.valuation_out_account_id:
            acc_src = move.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts['stock_account_input']

        if move.location_dest_id.valuation_in_account_id:
            acc_dest = move.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts['stock_account_output']

        # first get valuation account on the duty zone
        if type == 'incoming' and dest_zone and dest_zone.val_account_id:
            acc_valuation = dest_zone.val_account_id.id
        elif type == 'outgoing' and src_zone and src_zone.val_account_id:
            acc_valuation = src_zone.val_account_id.id
        else:
            acc_valuation = accounts.get('property_stock_valuation_account_id', False)

        # first check the destination location: get the right journel
        if type == 'incoming' and dest_zone and dest_zone.journal_id:
            journal_id = dest_zone.journal_id.id
        elif type == 'outgoing' and src_zone and src_zone.journal_id:
            journal_id = src_zone.journal_id.id
        else:
            journal_id = accounts['stock_journal']
        if acc_dest == acc_valuation:
            raise osv.except_osv(
                _('Error!'),
                _('Cannot create Journal Entry, Output Account of this '
                    'product and Valuation account on category of this product are same.'))

        if acc_src == acc_valuation:
            raise osv.except_osv(
                _('Error!'),
                _('Cannot create Journal Entry, '
                    'Input Account of this product and '
                    'Valuation account on category of this product are same.'))
        if not acc_src:
            raise osv.except_osv(
                _('Error!'),
                _('Please define stock input account '
                    'for this product or its category: "%s" (id: %d)') %
                (move.product_id.name, move.product_id.id,))
        if not acc_dest:
            raise osv.except_osv(
                _('Error!'),
                _('Please define stock output account for '
                    'this product or its category: "%s" (id: %d)') %
                (move.product_id.name, move.product_id.id,))
        if not journal_id:
            raise osv.except_osv(
                _('Error!'),
                _('Please define journal on the product category: "%s" (id: %d)') %
                (move.product_id.categ_id.name, move.product_id.categ_id.id,))
        if not acc_valuation:
            raise osv.except_osv(
                _('Error!'),
                _('Please define inventory valuation '
                    'account on the product category: "%s" (id: %d)') %
                (move.product_id.categ_id.name, move.product_id.categ_id.id,))
        return journal_id, acc_src, acc_dest, acc_valuation

    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        '''
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.

        ----
        extended note:
        if the internal move from one duty zone to another duty zone or the same
        duty zone with extra landed costs, the account move should
        be Generated as well.

        --
        once the stock move is done (workflow: action_done), this function is called to create
            account move.
        '''
        # FIXME: product valuation should perhaps be a property?
        if move.product_id.valuation == 'real_time':
            if context is None:
                context = {}
            # currently there is no cross-company case.
            src_company_ctx = dict(context, force_company=move.location_id.company_id.id)
            dest_company_ctx = dict(context, force_company=move.location_dest_id.company_id.id)
            account_moves = []
            # Outgoing moves (or cross-company output part)
            # FIXME: might have internal -> inventory location loss.
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and
                     move.location_dest_id.usage != 'internal' or
                     move.location_id.company_id != move.location_dest_id.company_id):
                # we get the stock valuation account of the duty zone first.
                journal_id, acc_src, acc_dest, acc_valuation = \
                    self._get_accounts_duty_zone_valuation(cr, uid, move, 'outgoing', src_company_ctx)

                reference_amount, reference_currency_id = \
                    self._get_reference_accounting_values_for_valuation(
                        cr, uid, move, 'outgoing', src_company_ctx)
                #returning goods to supplier
                if move.location_dest_id.usage == 'supplier':
                    account_moves += \
                        [(journal_id, self._create_account_move_line(
                            cr, uid, move, acc_valuation, acc_src,
                            reference_amount, reference_currency_id, context))]
                else:
                    account_moves += \
                        [(journal_id, self._create_account_move_line(
                            cr, uid, move, acc_valuation, acc_dest,
                            reference_amount, reference_currency_id, context))]

            # Incoming moves (or cross-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage != 'internal' and
                     move.location_dest_id.usage == 'internal'
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = \
                    self._get_accounts_duty_zone_valuation(cr, uid, move, 'incoming', dest_company_ctx)

                # reference_amount depends on the right cost price.
                reference_amount, reference_currency_id = \
                    self._get_reference_accounting_values_for_valuation(
                        cr, uid, move, 'incoming', src_company_ctx)

                #goods return from customer
                if move.location_id.usage == 'customer':
                    account_moves += \
                        [(journal_id, self._create_account_move_line(
                            cr, uid, move, acc_dest, acc_valuation, reference_amount,
                            reference_currency_id, context))]
                else:
                    account_moves += \
                        [(journal_id, self._create_account_move_line(
                            cr, uid, move, acc_src, acc_valuation, reference_amount,
                            reference_currency_id, context))]

            # Internal moves: for every internal move with LC, we should have the account moves.
            #  - and change the average price accordingly.
            if move.company_id.support_duty_zone:
                src_zone, dest_zone = move.location_id.duty_zone_id, move.location_dest_id.duty_zone_id
                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal' \
                        and ((not src_zone) or (not dest_zone)):
                    #FIXME to complete the constraint
                    raise osv.except_osv(
                        _('Warning'),
                        _('You must forget to specify a duty zone'
                            ' to one of the locations: %s, %s') %
                        (move.location_id.complete_name, move.location_dest_id.complete_name))
                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal' \
                        and (move.landed_costs or self.check_if_cross_zone(move)):
                    journal_id, acc_src, acc_dest = \
                        dest_zone.journal_id.id, src_zone.val_account_id.id, dest_zone.val_account_id.id

                    reference_amount, reference_currency_id = \
                        self._get_reference_accounting_values_for_duty_internal(
                            cr, uid, move, src_company_ctx)
                    account_moves += \
                        [(journal_id, self._create_account_move_line(
                            cr, uid, move, acc_src, acc_dest, reference_amount,
                            reference_currency_id, context))]

            # in this case, we use the standard odoo cost price.
            # for the company which doesn't support duty zone.
            elif not move.company_id.support_duty_zone and move.landed_costs and \
                move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal':
                partner_id = (move.picking_id.partner_id and self.pool.get('res.partner')._find_accounting_partner(
                    move.picking_id.partner_id).id) or False
                journal_id, acc_src, acc_dest, acc_valuation = \
                    self._get_accounts_duty_zone_valuation(cr, uid, move, '', src_company_ctx)
                res = self._prepare_account_credit_lines_landed_cost(cr, uid, move, context=context)
                debit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id and move.product_id.id or False,
                    'quantity': 1,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': partner_id,
                    'debit': move.landed_costs,
                    'account_id': acc_valuation,
                    'credit': 0
                }
                res.append(debit_line_vals)
                move_lines = [(0, 0, m) for m in res]
                account_moves += \
                    [(journal_id, move_lines)]

            move_obj = self.pool.get('account.move')
            for j_id, move_lines in account_moves:
                move_obj.create(
                    cr, uid,
                    {'journal_id': j_id,
                     'line_id': move_lines,
                     'ref': move.picking_id and move.picking_id.name})

    def _get_reference_accounting_values_for_duty_internal(self, cr, uid, move, context=None):
        """
        Return the reference amount and reference currency representing
        the inventory valuation for this move.
        These reference values should possibly be converted before being posted in
        Journals to adapt to the primary and secondary currencies of the relevant accounts.

        ---
        This is specific for internal move of cross duty zones.
        So the move must be internal.
        """
        assert move.location_id.usage == 'internal'
        assert move.location_dest_id.usage == 'internal'
        src_zone, dest_zone = move.location_id.duty_zone_id, move.location_dest_id.duty_zone_id
        src_price_type, dest_price_type = src_zone.price_type_id, dest_zone.price_type_id
        product_uom_obj = self.pool.get('product.uom')

        # by default the reference currency is that of the move's company
        reference_currency_id = move.company_id.currency_id.id

        default_uom = move.product_id.uom_id.id
        qty = product_uom_obj._compute_qty(
            cr, uid, move.product_uom.id, move.product_qty, default_uom)

        if context is None:
            context = {}
        currency_ctx = dict(context, currency_id=move.company_id.currency_id.id)
        amount_unit = move.product_id.price_get(
            src_price_type.field, context=currency_ctx)[move.product_id.id]
        reference_amount = amount_unit * qty

        return reference_amount, reference_currency_id

    def _prepare_account_credit_lines_landed_cost(self, cr, uid, move, context=None):
        '''Split the landed costs for each stock move.
        1- prepare the distributed value for landed costs from order.
        2- prepare the credit lines for landed costs on each stock move'''
        res = []
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account') + 5
        prod_obj = self.pool.get('product.product')
        tot_value = 0.0
        total = 0
        #
        # create account moves for landed costs from picking level.
        #
        if move.landing_costs_order:
            # way of calculate the total value
            for m in move.picking_id.move_lines:
                tot_value += m.product_id.standard_price * m.product_qty
            assert move.picking_id, 'If we have landing cost from order,'
            ' the stock must have picking_id!'
            order = move.picking_id
            for landed_cost in move.picking_id.landed_cost_line_ids:
                landed_costs = 0
                # Base value (value from purchase order)
                if landed_cost.distribution_type_id.landed_cost_type == 'value' and order.purchase_id:
                    try:
                        # use the price with taxes
                        landed_costs += round(
                            order.landed_cost_base_value * move.purchase_line_subtotal /
                            order.purchase_id.amount_untaxed, prec)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError! computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s. (The total value of the stock picking might be zero.)' %
                            (move.name, move.picking_id.name))
                
                # Base value (cost price of the product)
                elif landed_cost.distribution_type_id.landed_cost_type == 'value' and not order.purchase_id:
                    try:
                        landed_costs += round((order.landed_cost_base_value * move.product_id.standard_price *
                                         move.product_qty / tot_value), prec)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError! computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s. (The total value of the stock picking might be zero.)' %
                            (move.name, move.picking_id.name))
                
                # Base Quantity (quantity from purchase order)
                elif landed_cost.distribution_type_id.landed_cost_type == 'per_unit' and order.purchase_id:
                    try:
                        # use the price with taxes
                        landed_costs += round(
                            landed_cost.amount * move.purchase_line_id.product_qty /
                            order.purchase_id.quantity_total, prec)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError! computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s. (The total value of the stock picking might be zero.)' %
                            (move.name, move.picking_id.name))
                # Base quantity (Per Quantity on stock picking)
                elif landed_cost.distribution_type_id.landed_cost_type == 'per_unit' and not order.purchase_id:
                    try:
                        landed_costs = round(landed_cost.amount * move.product_qty /
                                             order.quantity_total, prec)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError, computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s' % (move.name, move.picking_id.name))
                
                # Base Volume (volume from purchase order)
                elif landed_cost.distribution_type_id.landed_cost_type == 'volume' and order.purchase_id:
                    try:
                        landed_costs = round(landed_cost.amount * move.purchase_line_id.line_volume /
                                             order.volume_total, prec)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError, computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s' % (move.name, move.picking_id.name))
                # Base Volume (volume from stock picking)
                elif landed_cost.distribution_type_id.landed_cost_type == 'volume':
                    try:
                        landed_costs = round(landed_cost.amount * move.line_volume /
                                             order.volume_total, prec)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        _logger.error(
                            'ZeroDivisionError, computing the landing cost from order for stock" + \
                            "move: %s of stock picking: %s' % (move.name, move.picking_id.name))
                lc_account_id = prod_obj._choose_exp_account_from(
                    cr, uid, landed_cost.product_id, context=context)
                res.append({
                    'name': landed_cost.product_id.name,
                    'product_id': landed_cost.product_id and landed_cost.product_id.id or False,
                    'quantity': 1.0,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': landed_cost.partner_id.id,
                    'credit': landed_costs,
                    'debit': 0,
                    'account_id': lc_account_id,
                })
                total += landed_costs
        #
        # create account moves for landed costs on stock move level.
        #
        if move.landing_costs:
            for landed_cost in move.landed_cost_line_ids:
                if landed_cost.distribution_type_id.landed_cost_type == 'value':
                    landed_costs = landed_cost.amount
                elif landed_cost.distribution_type_id.landed_cost_type == 'volume':
                    landed_costs = move.line_volume * landed_cost.amount
                else:
                    landed_costs = move.product_qty * landed_cost.amount
                lc_account_id = prod_obj._choose_exp_account_from(
                    cr, uid, landed_cost.product_id, context=context)
                res.append({
                    'name': landed_cost.product_id.name,
                    'product_id': landed_cost.product_id and landed_cost.product_id.id or False,
                    'quantity': 1.0,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': landed_cost.partner_id.id,
                    'credit': landed_costs,
                    'debit': 0,
                    'account_id': lc_account_id,
                })
                total += landed_costs
        return res

    def _create_account_move_line(
            self, cr, uid, move, src_account_id, dest_account_id, reference_amount,
            reference_currency_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given stock move.
        :param reference_amount: the total cost value of the product.

        for Outgoing and Incoming shipment.
        and extra landed costs.
        """
        # prepare default values considering that the destination accounts have the reference_currency_id as their main currency
        partner_id = (move.picking_id.partner_id and self.pool.get('res.partner')._find_accounting_partner(move.picking_id.partner_id).id) or False
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        
        # if we are posting to accounts in a different currency, provide correct values in both currencies correctly
        # when compatible with the optional secondary currency on the account.
        # Financial Accounts only accept amounts in secondary currencies if there's no secondary currency on the account
        # or if it's the same as that of the secondary amount being posted.
        account_obj = self.pool.get('account.account')
        src_acct, dest_acct = account_obj.browse(cr, uid, [src_account_id, dest_account_id], context=context)
        src_main_currency_id = src_acct.company_id.currency_id.id
        dest_main_currency_id = dest_acct.company_id.currency_id.id
        cur_obj = self.pool.get('res.currency')
        debit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id and move.product_id.id or False,
                    'quantity': move.product_qty,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': partner_id,
                    'debit': reference_amount,
                    'account_id': dest_account_id,
                    'credit': 0
        }
        if reference_currency_id != dest_main_currency_id:
            # fix debit line:
            debit_line_vals['debit'] = cur_obj.compute(
                cr, uid, reference_currency_id, dest_main_currency_id,
                reference_amount, context=context)
        
        credit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id and move.product_id.id or False,
                    'quantity': move.product_qty,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': partner_id,
                    'credit': reference_amount,
                    'debit': 0,
                    'account_id': src_account_id,
        }
        #The account should be the expense account of the product.
        credit_lc_line_vals = self._prepare_account_credit_lines_landed_cost(
            cr, uid, move, context=context)
        if reference_currency_id != src_main_currency_id:
            # fix credit line:
            credit_line_vals['credit'] = cur_obj.compute(
                cr, uid, reference_currency_id, src_main_currency_id,
                reference_amount, context=context)
            if (not src_acct.currency_id) or src_acct.currency_id.id == reference_currency_id:
                credit_line_vals.update(
                    currency_id=reference_currency_id, amount_currency=-reference_amount)

        move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        if credit_lc_line_vals:
            landed_costs = 0
            for lc in credit_lc_line_vals:
                landed_costs += round(lc['credit'], prec)
            # the currency of landed costs is the same as company's default one.
            # we sum the landed costs up to avoid rounding issue
            debit_line_vals['debit'] += landed_costs

            move_lines.extend([(0, 0, lc_lines) for lc_lines in credit_lc_line_vals])
        return move_lines

    def check_if_cross_zone(self, move):
        '''Check if all the moves have:
            * cross zone
        :param pick: browse_record object of stock_picking'''
        if move.location_id.usage != "internal" or move.location_dest_id.usage != 'internal':
            return False
        src_zone, dest_zone = move.location_id.duty_zone_id, move.location_dest_id.duty_zone_id
        assert (src_zone and dest_zone), 'One of The duty zones of the locations:%s, %s has not been set.' % \
            (move.location_id.complete_name, move.location_dest_id.complete_name)
        if (src_zone.id != dest_zone.id):
            return True
        return False


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _get_valid_rules(self, move, rules):
        '''get the matched rules according to the locations'''
        val = []
        if not rules:
            return val
        for rule in rules:
            if (rule.src_location_id) and (rule.src_location_id.id != move.location_id.id):
                continue
            elif (rule.dest_location_id) and \
                    (rule.dest_location_id.id != move.location_dest_id.id):
                continue
            else:
                val.append(rule)
        return val

    def compute_rule(self, cr, uid, rule, localdict, context=None):
        """
        :param rule: rule record
        :param localdict: dictionary containing the environement in which to compute the rule
        :return: returns a tuple build as the base/amount computed, the quantity and the rate
        :rtype: (float, float, float)
        """
        # rule = self.browse(cr, uid, rule_id, context=context)
        if rule.amount_select == 'fix':
            try:
                return rule.amount_fix, eval(rule.quantity, localdict), 100.0
            except:
                raise osv.except_osv(
                    _('Error!'),
                    _('Wrong quantity defined for duty rule %s.') % (rule.name))

        elif rule.amount_select == 'percentage':
            try:
                return eval(rule.amount_percentage_base, localdict), \
                    eval(rule.quantity, localdict), \
                    rule.amount_percentage
            except:
                raise osv.except_osv(
                    _('Error!'),
                    _('Wrong percentage base or quantity'
                        ' defined for duty rule %s.') % (rule.name))
        else:
            try:
                eval(rule.amount_python_compute, localdict, mode='exec', nocopy=True)
                return localdict['result'], \
                    'result_qty' in localdict and localdict['result_qty'] or 1.0, \
                    'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise osv.except_osv(
                    _('Error!'),
                    _('Wrong python code defined for'
                        ' duty rule %s.') % (rule.name))

    def _get_default_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.currency_id.id

    # TODO the date of the currency computation, which date should we use?
    def _compute_currency_amount(
            self, cr, uid, amount_currency, currency_id, to_currency_id, date, context=None):
        cur_obj = self.pool.get('res.currency')
        amount = amount_currency
        if currency_id != to_currency_id:
            ctx = context.copy()
            ctx['date'] = date or False
            amount = cur_obj.compute(
                cr, uid, currency_id, to_currency_id, amount, context=ctx)
        return amount

    def get_landed_cost_lines(self, cr, uid, moves=False, context=None):
        """
        :param move_id: ids of stock moves.
        :return:
        :rtype: False or [{'field1': val1, ...}, {'field2': val2, ...}, ...]
        """
        if not moves:
            return False
        matched_rules = []
        res = {}
        localdict = {}
        # this is the company's default currency.
        default_currency = self._get_default_currency(cr, uid, context=context)

        for move in moves:
            res[move.id] = []
            # this is used in python code.
            localdict['product'] = move.product_id
            rules = move.product_id.duty_rule_ids
            matched_rules = self._get_valid_rules(move, rules)
            for rule in matched_rules:
                amount, qty, rate = self.compute_rule(cr, uid, rule, localdict, context=context)
                tot_amount = amount * qty * rate / 100.0
                landed_cost_val = {
                    'name': move.name,
                    'product_id': rule.product_id.id,
                    'partner_id': rule.partner_id.id,
                    'generate_invoice': rule.generate_invoice,
                    'amount_currency': tot_amount,
                    'currency_id': rule.currency_id.id,
                    'company_id': rule.company_id.id,
                    'distribution_type_id': rule.distribution_type_id.id,
                    'amount': self._compute_currency_amount(
                        cr, uid, tot_amount, rule.currency_id.id,
                        default_currency, move.create_date, context=context),
                    'rule_id': rule.id,
                    'invoice_total_per_product': rule.invoice_total_per_product
                }
                res[move.id].append(landed_cost_val)
        return res

    def compute_landed_costs(self, cr, uid, moves, context=None):
        '''create the automatic landed cost for stock moves.
        [return]: True or False'''
        moves = [m for m in moves if not m.duty_rule_computed]
        res = self.get_landed_cost_lines(cr, uid, moves, context=context)
        for move in moves:
            if res[move.id]:
                val = [(0, 0, l) for l in res[move.id]]
                move.write({'landed_cost_line_ids': val, 'duty_rule_computed': True})
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        '''To compute the automatic landed costs according to the duty rules on product'''
        for picking in self.browse(cr, uid, ids, context=context):
            if not picking.duty_rule_computed:
                self.compute_landed_costs(cr, uid, picking.move_lines, context=context)
            else:
                _logger.debug('-----the automatic landed cost has already" +\
                    " been computed, please check! Picking: %s, %d ' % (picking.name, picking.id))
        return super(stock_picking, self).action_confirm(
            cr, uid, ids, context=context)

    def _landed_cost_base_volume(self, cr, uid, ids, name, args, context=None):
        '''get total landed costs based on volume'''
        if not ids:
            return {}
        result = {}
        for order in self.browse(cr, uid, ids, context=context):
            landed_costs_base_volume = 0.0
            if order.landed_cost_line_ids:
                for costs in order.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'volume' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_volume += costs.amount
            result[order.id] = landed_costs_base_volume
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        '''Get the total landed costs'''
        if not ids:
            return {}
        result = {}
        # landed costs for the pickings
        for order in self.browse(cr, uid, ids, context=context):
            landed_costs = 0.0
            landed_costs += (order.landing_cost_lines +
                             order.landed_cost_base_value +
                             order.landed_cost_base_quantity +
                             order.landed_cost_base_volume)
            result[order.id] = landed_costs
        return result

    def _volume_total(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for order in self.browse(cr, uid, ids, context=context):
            volume_total = 0.0
            if order.move_lines:
                for move_line in order.move_lines:
                    if move_line.line_volume > 0.0:
                        volume_total += move_line.line_volume
            result[order.id] = volume_total
        return result

    def _quantity_total(self, cr, uid, ids, name, args, context=None):
        '''calculate the total quantity of the pruducts
        TOFIX: fix parent module: purchase_landed_costs's bug:
            variable:quantity_total should be inited in the loop!!
        '''
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            quantity_total = 0.0
            if not line.move_lines:
                result[line.id] = quantity_total
                continue
            for move_line in line.move_lines:
                if move_line.product_qty > 0.0:
                    quantity_total += move_line.product_qty
            result[line.id] = quantity_total
        return result

    def _landed_cost_base_value(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs_base_value = 0.0
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'value' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_value += costs.amount
            result[line.id] = landed_costs_base_value
        return result

    def _landed_cost_base_quantity(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        landed_costs_base_quantity = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'per_unit' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_quantity += costs.amount
            result[line.id] = landed_costs_base_quantity
        return result

    def _landing_cost_lines(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            landed_cost_lines = 0.0
            if not line.move_lines:
                result[line.id] = landed_cost_lines
                continue
            for move_line in line.move_lines:
                # TODO to be checked if necessary
                if move_line.product_qty > 0.0:
                    landed_cost_lines += move_line.landing_costs
            result[line.id] = landed_cost_lines
        return result

    def _get_duty_rule_computed(self, cr, uid, ids, name, args, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = True
            for move in picking.move_lines:
                if not move.duty_rule_computed:
                    res[picking.id] = False
        return res

    _columns = {
        'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'picking_id',
            'Landed Costs',),
        'landed_cost_base_value': fields.function(
            _landed_cost_base_value,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Value'),
        'landed_cost_base_quantity': fields.function(
            _landed_cost_base_quantity,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Quantity'),
        'landing_cost_lines': fields.function(
            _landing_cost_lines,
            digits_compute=dp.get_precision('Account'),
            string='Landing Cost Lines'),
        'landed_cost': fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Total'),
        'quantity_total': fields.function(
            _quantity_total,
            digits_compute=dp.get_precision('Product UoM'),
            string='Total Quantity'),
        'volume_total': fields.function(
            _volume_total,
            digits_compute=dp.get_precision('Volume Factor'),
            string="Total Volume"),
        'landed_cost_base_volume': fields.function(
            _landed_cost_base_volume,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Volume'),
        'duty_rule_computed': fields.function(
            _get_duty_rule_computed,
            type='boolean',
            string='Duty Rule Computed'),
        'currency_id': fields.related(
            'company_id', 'currency_id',
            type='many2one', relation='res.currency', string='Currency', readonly=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        res = super(stock_picking, self).copy_data(
            cr, uid, id, default, context)
        if 'move_lines' in res:
            moves = res['move_lines']
            for m in moves:
                assert len(m) == 3, 'The length of the move line tuple is not 3!'
                del m[2]['landed_cost_line_ids']
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        '''rewrite the copy method to avoid copy the field: duty_rule_computed'''
        default = default or {}
        default.update(
            {'duty_rule_computed': False,
             'landed_cost_line_ids': [],
             })
        return super(stock_picking, self).copy(
            cr, uid, id, default, context=context)

    def LC_copy_backorder(self, cr, uid, move, new_move_id, context=None):
        '''
        :param move: browse_record object of stock_move. current src_move
        :param new_move_id: id of new stock move
        :return: new created lc ids'''
        #
        lc_obj = self.pool.get('landed.cost.position')
        new_lc_ids = []
        for m_lc in move.landed_cost_line_ids:
            dist_type = m_lc.distribution_type_id
            # we unlink the with simple landed cost generated from rules.
            # because it will be generated for new move after confirm.
            if m_lc.rule_id and dist_type.landed_cost_type == 'value':
                m_lc.unlink()
            # copy the LC distributed by quantity/volume
            # and move the ones distributed by value to move.
            if not m_lc.rule_id:
                if dist_type.landed_cost_type == 'value':
                    m_lc.write({'move_id': new_move_id})
                else:
                    defaults = {
                        'move_id': new_move_id,
                        'purchase_order_info_id': m_lc.purchase_order_info_id and
                        m_lc.purchase_order_info_id.id or False,
                        'picking_info_id': m_lc.picking_info_id and
                        m_lc.picking_info_id.id or False
                    }
                    lc_val = lc_obj.copy_data(cr, uid, m_lc.id, defaults, context=context)
                    lc_id = lc_obj.create(cr, uid, lc_val, context=context)
                    new_lc_ids.append(lc_id)
        return new_lc_ids

    #
    # update the average price.
    #
    # FIXME: needs refactoring, this code is partially duplicated in stock_move.do_partial()!
    # check the modules who rewrite these method:
    #   stock_return_with_location and purchase_landed_cost_extended

    # update the new average prices.
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
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
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % (move.id), {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                #
                # recalculate the unit price for the move when it is partially received.
                # this is only for IS from purchase order.
                if move.purchase_line_id and product_qty < move.purchase_line_id.product_qty and product_qty != 0:
                    purchase_price = move.purchase_line_id.price_unit
                    purchase_qty = move.purchase_line_id.product_qty
                    purchase_price_untax = move.purchase_line_id.price_subtotal / move.purchase_line_id.product_qty
                    product_price = (move.purchase_line_id.landed_costs - (purchase_qty - product_qty)
                                     * purchase_price_untax) / product_qty
                product_currency = partial_data.get('product_currency', False)
                # for warning and later on check if other unexpected case.
                if product_uom and (product_uom != move.product_id.uom_id.id):
                    _logger.warning('module:stock_landed_costs.\n'
                                    'the uom of the stock move is not the same as product.'
                                    'Please check the move: %d' % move.id)
                if product_currency and (product_currency != move.company_id.currency_id.id):
                    _logger.warning('module:stock_landed_costs.\n'
                                    'the currency of the stock move is not the same as product.'
                                    'Please check the move: %d' % move.id)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(
                    cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                location_obj = self.pool.get('stock.location')
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = move.product_id
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                    # get the qty of available Alex (from module: purchase_landed_cost_extended)
                    #
                    # re-implemented this method, add a new param: domain
                    # Note: if extract this module, the function need to be in the new module.
                    #
                    product_qty_available = location_obj.get_product_qty_of_checked_locations(
                        cr, uid, [],
                        move.product_id.id, domain=[], context=context, states=['done']).get(
                        move.product_id.id, 0.0)

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product_qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_qty_available)\
                                + (new_price * qty))/(product_qty_available + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
                    #
                    # for the new cost price computation incoming)
                    #
                    if move.company_id.support_duty_zone:
                        dest_zone = move.location_dest_id.duty_zone_id
                        price_name = dest_zone.price_type_id.field
                        product_qty_available = 0
                        product_qty_available = location_obj.get_product_qty_of_checked_locations(
                            cr, uid, [],
                            move.product_id.id, domain=[('duty_zone_id', '=', dest_zone.id)],
                            context=context, states=['done']).get(
                            move.product_id.id, 0.0)

                        if qty > 0 and dest_zone:
                            # update the transit cost price. PP + landed cost (stock move)
                            if move.purchase_line_id:
                                # move.price_unit purchase price on purchase order.
                                new_price = (move.price_unit * qty + move.landed_costs) / qty
                                # convert the price.
                                new_price = currency_obj.compute(cr, uid, product_currency,
                                        move_currency_id, product_price)
                                new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                    product.uom_id.id)
                                if product_qty_available <= 0:
                                    new_std_price = new_price
                                else:
                                    amount_unit = product.price_get(price_name, context=context)[product.id]
                                    new_std_price = ((amount_unit * product_qty_available)
                                        + (new_price * qty)) / (product_qty_available + qty)
                                # Write the field according to price type field
                                product_obj.write(cr, uid, [product.id], {price_name: new_std_price})

                            else:
                                # FIXME in this case is: manually created incoming shipment.
                                _logger.debug('When calculating average price, There is no '
                                              'purchase order line in the '
                                              'stock move %s, %d' % (move.name, move.id))
                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    # move_obj.write(
                    #     cr, uid, [move.id],
                    #     {'price_unit': product_price,
                    #      'price_currency_id': product_currency})
                # case: internal move with LC (update standard cost price and duty zone cost price)
                # If with LC, we update the standard cost price as well.
                #
                elif (pick.type == 'internal') and (move.product_id.cost_method == 'average') and \
                        pick.landed_cost:
                    product = move.product_id
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    # update standard cost price
                    product_qty_available = 0
                    product_qty_available = location_obj.get_product_qty_of_checked_locations(
                        cr, uid, [],
                        move.product_id.id, domain=[],
                        context=context, states=['done']).get(
                        move.product_id.id, 0.0)
                    if qty > 0:
                        product_price = (move.product_id.standard_price * qty + move.landed_costs) / qty
                        new_price = currency_obj.compute(
                            cr, uid, product_currency,
                            move_currency_id, product_price)
                        new_price = uom_obj._compute_price(
                            cr, uid, product_uom, new_price,
                            product.uom_id.id)
                        if product_qty_available <= 0:
                            new_std_price = new_price
                        else:
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            # if it is internal move, The total quantity doesn't change.
                            new_std_price = ((amount_unit * product_qty_available + move.landed_costs)
                                             / product_qty_available)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                    # update the new cost prices
                    if move.company_id.support_duty_zone:
                        dest_zone = move.location_dest_id.duty_zone_id
                        src_zone = move.location_id.duty_zone_id
                        price_dest_name = dest_zone.price_type_id.field
                        price_src_name = src_zone.price_type_id.field
                        product_qty_available = location_obj.get_product_qty_of_checked_locations(
                            cr, uid, [],
                            move.product_id.id, domain=[('duty_zone_id', '=', dest_zone.id)],
                            context=context, states=['done']).get(
                            move.product_id.id, 0.0)

                        if qty > 0:
                            # get the new price: AP + landed cost
                            # TODO check conversion of currency and uom is right
                            product_price = (getattr(move.product_id, price_src_name) * qty + move.landed_costs) / qty
                            new_price = currency_obj.compute(
                                cr, uid, product_currency,
                                move_currency_id, product_price)
                            new_price = uom_obj._compute_price(
                                cr, uid, product_uom, new_price,
                                product.uom_id.id)
                            if product_qty_available <= 0:
                                new_std_price = new_price
                            else:
                                # Get the old cost price on the dest duty zone.
                                amount_unit = product.price_get(price_dest_name, context=context)[product.id]
                                if self.check_if_cross_zone(pick):
                                    new_std_price = ((amount_unit * product_qty_available)
                                                     + (new_price * qty)) / (product_qty_available + qty)
                                # if it is the same zone, The total quantity doesn't change.
                                else:
                                    new_std_price = ((amount_unit * product_qty_available + move.landed_costs)
                                                     / (product_qty_available))
                            # Write the field according to price type field
                            product_obj.write(cr, uid, [product.id], {price_dest_name: new_std_price})
                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    move_obj.write(
                        cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency})

                # case: if we don't have the landed cost but it's cross zone move.
                # no need to update standard cost price, update the dest zone cost price.
                elif (pick.type == 'internal') and (move.product_id.cost_method == 'average') and \
                        move.company_id.support_duty_zone and move_obj.check_if_cross_zone(move):
                    dest_zone = move.location_dest_id.duty_zone_id
                    src_zone = move.location_id.duty_zone_id
                    price_dest_name = dest_zone.price_type_id.field
                    price_src_name = src_zone.price_type_id.field
                    product = move.product_id

                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    product_qty_available = location_obj.get_product_qty_of_checked_locations(
                        cr, uid, [],
                        move.product_id.id, domain=[('duty_zone_id', '=', dest_zone.id)],
                        context=context, states=['done']).get(
                        move.product_id.id, 0.0)

                    if qty > 0:
                        # get the new price: AP of src zone + landed cost
                        # TODO check conversion of currency and uom is right
                        product_price = (getattr(move.product_id, price_src_name) * qty + move.landed_costs) / qty
                        new_price = currency_obj.compute(
                            cr, uid, product_currency,
                            move_currency_id, product_price)
                        new_price = uom_obj._compute_price(
                            cr, uid, product_uom, new_price,
                            product.uom_id.id)
                        if product_qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the old cost price on the dest duty zone.
                            amount_unit = product.price_get(price_dest_name, context=context)[product.id]
                            if self.check_if_cross_zone(pick):
                                new_std_price = ((amount_unit * product_qty_available)
                                                 + (new_price * qty)) / (product_qty_available + qty)
                            # if it is the same zone, The total quantity doesn't change.
                            else:
                                new_std_price = ((amount_unit * product_qty_available + move.landed_costs)
                                                 / (product_qty_available))
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {price_dest_name: new_std_price})

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    move_obj.write(
                        cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency})
            
            for move in too_few:
                product_qty = move_product_qty[move.id]
                new_move = None
                if not new_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id], 
                               {'name': sequence_obj.get(
                                cr, uid, 'stock.picking%s' % (pick.type != 'internal' and '.' + pick.type or '')),
                               })
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    new_move = move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                            'prodlot_id': False,
                            'tracking_id': False,
                        })
                #
                # we unlink the with simple landed cost generated from rules
                if new_move:
                    self.LC_copy_backorder(cr, uid, move, new_move, context=context)

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # we always put the landed costs to the first partial move.
            # before we confirm the new picking, we copy the landed costs.
            if new_picking:
                for lc in pick.landed_cost_line_ids:
                    lc.write(
                        {'picking_id': new_picking, 'picking_info_id': new_picking}, context=context)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
                back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                self.message_post(cr, uid, ids, body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
            else:
                self.action_move(cr, uid, [pick.id], context=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}
        return res

    def check_if_cross_zone(self, pick):
        '''Check if all the moves of this pick have:
            * the same location and dest location
            * cross zone
        :param pick: browse_record object of stock_picking'''
        move_obj = self.pool.get('stock.move')
        for move in pick.move_lines:
            if not move_obj.check_if_cross_zone(move):
                return False
        return True


class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'

    def _landed_cost_base_volume(self, cr, uid, ids, name, args, context=None):
        '''get total landed costs based on volume'''
        if not ids:
            return {}
        result = {}
        for order in self.browse(cr, uid, ids, context=context):
            landed_costs_base_volume = 0.0
            if order.landed_cost_line_ids:
                for costs in order.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'volume' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_volume += costs.amount
            result[order.id] = landed_costs_base_volume
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        '''Get the total landed costs'''
        if not ids:
            return {}
        result = {}
        # landed costs for the pickings
        for order in self.browse(cr, uid, ids, context=context):
            landed_costs = 0.0
            landed_costs += (order.landing_cost_lines +
                             order.landed_cost_base_value +
                             order.landed_cost_base_quantity +
                             order.landed_cost_base_volume)
            result[order.id] = landed_costs
        return result

    def _volume_total(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for order in self.browse(cr, uid, ids, context=context):
            volume_total = 0.0
            if order.move_lines:
                for move_line in order.move_lines:
                    if move_line.line_volume > 0.0:
                        volume_total += move_line.line_volume
            result[order.id] = volume_total
        return result

    def _quantity_total(self, cr, uid, ids, name, args, context=None):
        '''calculate the total quantity of the pruducts
        TOFIX: fix parent module: purchase_landed_costs's bug:
            variable:quantity_total should be inited in the loop!!
        '''
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            quantity_total = 0.0
            if not line.move_lines:
                result[line.id] = quantity_total
                continue
            for move_line in line.move_lines:
                if move_line.product_qty > 0.0:
                    quantity_total += move_line.product_qty
            result[line.id] = quantity_total
        return result

    def _landed_cost_base_value(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs_base_value = 0.0
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'value' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_value += costs.amount
            result[line.id] = landed_costs_base_value
        return result

    def _landed_cost_base_quantity(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        landed_costs_base_quantity = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'per_unit' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_quantity += costs.amount
            result[line.id] = landed_costs_base_quantity
        return result

    def _landing_cost_lines(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            landed_cost_lines = 0.0
            if not line.move_lines:
                result[line.id] = landed_cost_lines
                continue
            for move_line in line.move_lines:
                # TODO to be checked if necessary
                if move_line.product_qty > 0.0:
                    landed_cost_lines += move_line.landing_costs
            result[line.id] = landed_cost_lines
        return result

    def _get_duty_rule_computed(self, cr, uid, ids, name, args, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = True
            for move in picking.move_lines:
                if not move.duty_rule_computed:
                    res[picking.id] = False
        return res
    _columns = {
        'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'picking_id',
            'Landed Costs',),
        'landed_cost_base_value': fields.function(
            _landed_cost_base_value,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Value'),
        'landed_cost_base_quantity': fields.function(
            _landed_cost_base_quantity,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Quantity'),
        'landing_cost_lines': fields.function(
            _landing_cost_lines,
            digits_compute=dp.get_precision('Account'),
            string='Landing Cost Lines'),
        'landed_cost': fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Total'),
        'quantity_total': fields.function(
            _quantity_total,
            digits_compute=dp.get_precision('Product UoM'),
            string='Total Quantity'),
        'volume_total': fields.function(
            _volume_total,
            digits_compute=dp.get_precision('Volume Factor'),
            string="Total Volume"),
        'landed_cost_base_volume': fields.function(
            _landed_cost_base_volume,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Volume'),
        'duty_rule_computed': fields.function(
            _get_duty_rule_computed,
            type='boolean',
            string='Duty Rule Computed'),
        'currency_id': fields.related(
            'company_id', 'currency_id',
            type='many2one', relation='res.currency', string='Currency', readonly=True),
    }


# class stock_picking_out(orm.Model):
#     _inherit = 'stock.picking.out'

#     def _landed_cost_base_volume(self, cr, uid, ids, name, args, context=None):
#         '''get total landed costs based on volume'''
#         if not ids:
#             return {}
#         result = {}
#         for order in self.browse(cr, uid, ids, context=context):
#             landed_costs_base_volume = 0.0
#             if order.landed_cost_line_ids:
#                 for costs in order.landed_cost_line_ids:
#                     if (costs.distribution_type_id.landed_cost_type == 'volume' and
#                             costs.distribution_type_id.apply_on == 'order'):
#                         landed_costs_base_volume += costs.amount
#             result[order.id] = landed_costs_base_volume
#         return result

#     def _landed_cost(self, cr, uid, ids, name, args, context=None):
#         '''Get the total landed costs'''
#         if not ids:
#             return {}
#         result = {}
#         # landed costs for the pickings
#         for order in self.browse(cr, uid, ids, context=context):
#             landed_costs = 0.0
#             landed_costs += (order.landing_cost_lines +
#                              order.landed_cost_base_value +
#                              order.landed_cost_base_quantity +
#                              order.landed_cost_base_volume)
#             result[order.id] = landed_costs
#         return result

#     def _volume_total(self, cr, uid, ids, name, args, context=None):
#         if not ids:
#             return {}
#         result = {}
#         for order in self.browse(cr, uid, ids, context=context):
#             volume_total = 0.0
#             if order.move_lines:
#                 for move_line in order.move_lines:
#                     if move_line.line_volume > 0.0:
#                         volume_total += move_line.line_volume
#             result[order.id] = volume_total
#         return result

#     def _quantity_total(self, cr, uid, ids, name, args, context=None):
#         '''calculate the total quantity of the pruducts
#         TOFIX: fix parent module: purchase_landed_costs's bug:
#             variable:quantity_total should be inited in the loop!!
#         '''
#         if not ids:
#             return {}
#         result = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             quantity_total = 0.0
#             if not line.move_lines:
#                 result[line.id] = quantity_total
#                 continue
#             for move_line in line.move_lines:
#                 if move_line.product_qty > 0.0:
#                     quantity_total += move_line.product_qty
#             result[line.id] = quantity_total
#         return result

#     def _landed_cost_base_value(self, cr, uid, ids, name, args, context=None):
#         if not ids:
#             return {}
#         result = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             landed_costs_base_value = 0.0
#             if line.landed_cost_line_ids:
#                 for costs in line.landed_cost_line_ids:
#                     if (costs.distribution_type_id.landed_cost_type == 'value' and
#                             costs.distribution_type_id.apply_on == 'order'):
#                         landed_costs_base_value += costs.amount
#             result[line.id] = landed_costs_base_value
#         return result

#     def _landed_cost_base_quantity(self, cr, uid, ids, name, args, context=None):
#         if not ids:
#             return {}
#         result = {}
#         landed_costs_base_quantity = 0.0
#         for line in self.browse(cr, uid, ids, context=context):
#             if line.landed_cost_line_ids:
#                 for costs in line.landed_cost_line_ids:
#                     if (costs.distribution_type_id.landed_cost_type == 'per_unit' and
#                             costs.distribution_type_id.apply_on == 'order'):
#                         landed_costs_base_quantity += costs.amount
#             result[line.id] = landed_costs_base_quantity
#         return result

#     def _landing_cost_lines(self, cr, uid, ids, name, args, context=None):
#         if not ids:
#             return {}
#         result = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             landed_cost_lines = 0.0
#             if not line.move_lines:
#                 result[line.id] = landed_cost_lines
#                 continue
#             for move_line in line.move_lines:
#                 # TODO to be checked if necessary
#                 if move_line.product_qty > 0.0:
#                     landed_cost_lines += move_line.landing_costs
#             result[line.id] = landed_cost_lines
#         return result
#     _columns = {
#         'landed_cost_line_ids': fields.one2many(
#             'landed.cost.position',
#             'picking_id',
#             'Landed Costs',),
#         'landed_cost_base_value': fields.function(
#             _landed_cost_base_value,
#             digits_compute=dp.get_precision('Account'),
#             string='Landed Costs Base Value'),
#         'landed_cost_base_quantity': fields.function(
#             _landed_cost_base_quantity,
#             digits_compute=dp.get_precision('Account'),
#             string='Landed Costs Base Quantity'),
#         'landing_cost_lines': fields.function(
#             _landing_cost_lines,
#             digits_compute=dp.get_precision('Account'),
#             string='Landing Cost Lines'),
#         'landed_cost': fields.function(
#             _landed_cost,
#             digits_compute=dp.get_precision('Account'),
#             string='Landed Costs Total'),
#         'quantity_total': fields.function(
#             _quantity_total,
#             digits_compute=dp.get_precision('Product UoM'),
#             string='Total Quantity'),
#         'volume_total': fields.function(
#             _volume_total,
#             digits_compute=dp.get_precision('Volume Factor'),
#             string="Total Volume"),
#         'landed_cost_base_volume': fields.function(
#             _landed_cost_base_volume,
#             digits_compute=dp.get_precision('Account'),
#             string='Landed Costs Base Volume'),
#         'duty_rule_computed': fields.boolean('Duty Rule Computed'),
#         'currency_id': fields.related(
#             'company_id', 'currency_id',
#             type='many2one', relation='res.currency', string='Currency', readonly=True),
#     }

#     _defaults = {
#         'duty_rule_computed': False
#     }


class landed_cost_position(orm.Model):
    _inherit = 'landed.cost.position'

    def _get_picking_id(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.picking_id:
                result[record.id] = record.picking_id.id
            elif record.move_id:
                result[record.id] = record.move_id.picking_id and \
                    record.move_id.picking_id.id or False
            else:
                result[record.id] = False
        return result

    def _get_total_amount(self, cr, uid, landed_cost, context=None):
        """ We should have a field that is the computed value (total
        costs that land) e.g. if it's related to a line and per_unit =>
        I want for the reporting the total line landed cost and multiply
        the quantity by given amount.

        :param browse_record landed_cost: Landed cost position browse record
        :return total value of this landed cost position

        """
        vals_po_currency = 0.0
        if (landed_cost.purchase_order_line_id and
                landed_cost.distribution_type_id.landed_cost_type == 'per_unit'):
            vals_po_currency = (landed_cost.amount *
                                landed_cost.purchase_order_line_id.product_qty)
        else:
            vals_po_currency = landed_cost.amount
        return vals_po_currency

    def _get_amount_total(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        result = {}
        for landed_cost in self.browse(cr, uid, ids, context=context):
            if landed_cost.move_id:
                move = landed_cost.move_id
                if landed_cost.distribution_type_id.landed_cost_type == 'value':
                    landed_costs = landed_cost.amount
                elif landed_cost.distribution_type_id.landed_cost_type == 'volume':
                    landed_costs = move.line_volume * landed_cost.amount
                else:
                    landed_costs = move.product_qty * landed_cost.amount
            elif landed_cost.picking_id:
                landed_costs = landed_cost.amount
            result[landed_cost.id] = landed_costs
        return result

    _columns = {
        'origin': fields.char('Origin', size=256),
        'picking_id': fields.many2one(
            'stock.picking', 'Picking'),
        'purchase_order_info_id': fields.many2one(
            'purchase.order', 'Purchase Order'),
        'picking_info_id': fields.function(
            _get_picking_id, type='many2one',
            relation='stock.picking', string='Picking',
            readonly=True,
            store={
                'landed.cost.position': (lambda self, cr, uid, ids,c: ids, ['picking_id', 'move_id'], 10),
            }),
        'move_id': fields.many2one(
            'stock.move', 'Stock move'),
        'rule_id': fields.many2one('product.duty.rule', 'Rule'),
        'account_id': fields.many2one(
            'account.account',
            'Fiscal Account'),
        #TODO make the help message more helpful.
        'invoice_total_per_product': fields.boolean(
            "Total Per Product",
            help="When we invoice for this landing cost, "
            "whether we only create one invoice for one picking."),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'default_currency_id': fields.related(
            'company_id', 'currency_id', type='many2one',
            relation='res.currency', string='default Currency', store=True,
            readonly=True, help="This currency is used by amount, company's default currency."),
        # redefine these fields from module purchase_landed_costs.
        'amount_total_2': fields.function(
            _get_amount_total,
            type="float",
            digits_compute=dp.get_precision('Purchase Price'),
            string='Amount Total',
            help="This field represent the total amount of this position "
                 "regarding a whole order. By summing it, you'll have the total "
                 "landed cost for the order (in company's currency)",
        ),
    }

    _defaults = {
        'invoice_total_per_product': False,
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid, c).company_id.id
    }

    _order = "picking_info_id desc"

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if not partner_id:
            return {}
        partner = self.pool.get('res.partner').browse(
            cr, uid, partner_id, context=context)
        pricelist = partner.property_product_pricelist_purchase
        currency_id = pricelist.currency_id
        # FIX, the pricelist might not have currency
        return {'value': {'currency_id': currency_id and currency_id.id or False}}

    def _get_company_currency_from_landed_cost(self, cr, uid, landed_cost,
                                               amount, context=None):
        """ Return the amount in company currency by looking at the po.

        Always return a value, even if company currency = PO one.

        :param browse_record landed_cost: Landed cost position browse record
        :param float value to convert
        :return: Float value amount in company currency converted at po date

        rewrite this function: if the currency is the same as company's default one,
            no need to compute.

        """
        cur_obj = self.pool.get('res.currency')
        result = amount
        # In some cases, po is not set, we must take it back from po_line
        if landed_cost.purchase_order_id:
            po = landed_cost.purchase_order_id
        else:
            po = landed_cost.purchase_order_line_id.order_id
        if po:
            cmp_cur_id = po.company_id.currency_id.id
            lc_currency_id = landed_cost.currency_id and landed_cost.currency_id.id or False
            po_cur_id = po.pricelist_id.currency_id.id
            # first we check the user input amount
            if lc_currency_id and landed_cost.amount_currency and landed_cost.amount_currency and \
                    lc_currency_id == cmp_cur_id:
                return landed_cost.amount_currency

            if cmp_cur_id != po_cur_id:
                ctx = context.copy()
                ctx['date'] = landed_cost.date_po or False
                result = cur_obj.compute(cr, uid,
                                         po_cur_id,
                                         cmp_cur_id,
                                         landed_cost.amount,
                                         context=ctx)
        return result

    def onchange_product_id_picking(
        self, cr, uid, ids, product_id, partner_id,
            picking_id=False, context=None):
        """ Give the default value for the distribution type depending
        on the setting of the product and the use case: line or order
        position.

         """
        res = {}
        fiscal_position = False
        landed_cost_type = False
        # order or line depending on which view we are
        # get the fiscal_position we have.
        if partner_id:
            apply_on = 'order'
            partner_obj = self.pool.get('stock.picking')
            partner = partner_obj.browse(cr, uid, partner_id, context=context)
            fiscal_position = partner.property_account_position or False
        else:
            apply_on = 'line'
        if not product_id:
            return res
        prod_obj = self.pool.get('product.product')
        dist_type_obj = self.pool.get('landed.cost.distribution.type')
        prod = prod_obj.browse(cr, uid, [product_id], context=context)[0]
        account_id = prod_obj._choose_exp_account_from(
            cr, uid, prod, fiscal_position=fiscal_position, context=context)
        if prod.landed_cost_type in ('per_unit', 'value', 'volume'):
            landed_cost_type = dist_type_obj.search(
                cr, uid,
                [('apply_on', '=', apply_on),
                 ('landed_cost_type', '=', prod.landed_cost_type)],
                context=context)[0]
        value = {
            'distribution_type_id': landed_cost_type,
            'account_id': account_id,
            'partner_id': prod.seller_id and prod.seller_id.id or False
        }
        res = {'value': value}
        return res

    def onchange_amount_currency_picking(
        self, cr, uid, ids,
        amount_currency, currency_id,
            date_po, context=None):
        assert len(ids) < 2
        parent_currency_id = None
        parent_currency_id = self.pool.get('res.users').browse(
            cr, uid, uid, context).company_id.currency_id.id
        if not parent_currency_id or not amount_currency or not currency_id:
            return {}
        cur_obj = self.pool.get('res.currency')
        amount = amount_currency
        if currency_id != parent_currency_id:
            ctx = context.copy()
            ctx['date'] = date_po or False
            amount = cur_obj.compute(cr, uid,
                                     currency_id,
                                     parent_currency_id,
                                     amount,
                                     context=ctx)
        return {'value': {'amount': amount}}
