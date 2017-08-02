
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv
from tools.translate import _
import time

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    _name = "stock.partial.picking"
    _description = "Partial Picking with backorder fixed."
    _columns = {
        'product_moves_internal' : fields.one2many('stock.move.memory.internal', 'wizard_id', 'Moves'),
     }

    def get_picking_type(self, cr, uid, picking, context=None):
        picking_type = picking.type
        for move in picking.move_lines:
            if picking.type == 'in' and move.product_id.cost_method == 'average':
                picking_type = 'in'
                break
            # Don't touch the picking type because we also have 'internal'. Ian@Elico
            #else:
            #    picking_type = 'out'
        return picking_type

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        pick_obj = self.pool.get('stock.picking')
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        if not picking_ids:
            return res

        result = []
        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            pick_type = self.get_picking_type(cr, uid, pick, context=context)
            for m in pick.move_lines:
                if m.state in ('done', 'cancel'):
                    continue
                result.append(self.__create_partial_picking_memory(m, pick_type))

        if 'product_moves_in' in fields:
            res.update({'product_moves_in': result})
        if 'product_moves_out' in fields:
            res.update({'product_moves_out': result})
        # Add the internal Type. Ian@Elico
        if 'product_moves_internal' in fields:
            res.update({'product_moves_internal': result})        
        if 'date' in fields:
            res.update({'date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res

    def do_partial(self, cr, uid, ids, context=None):
        """ Makes partial moves and pickings done.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')

        picking_ids = context.get('active_ids', False)
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_datas = {
            'delivery_date' : partial.date
        }

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            picking_type = self.get_picking_type(cr, uid, pick, context=context)
            # Add internal type move. Ian@Elico: moves_list = picking_type == 'in' and partial.product_moves_in or partial.product_moves_out
            if picking_type == 'internal':
                moves_list = partial.product_moves_internal
            elif picking_type == 'out':
                moves_list = partial.product_moves_out
            else:
                moves_list = partial.product_moves_in
            # End of internal adding. Ian@Elico
            
            for move in moves_list:

                #Adding a check whether any line has been added with new qty
                if not move.move_id:
                    raise osv.except_osv(_('Processing Error'),\
                    _('You cannot add any new move while validating the picking, rather you can split the lines prior to validation!'))

                calc_qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, \
                                    move.quantity, move.move_id.product_uom.id)

                #Adding a check whether any move line contains exceeding qty to original moveline
#                if calc_qty > move.move_id.product_qty:
#                    raise osv.except_osv(_('Processing Error'),
#                    _('Processing quantity %d %s for %s is larger than the available quantity %d %s !')\
#                    %(move.quantity, move.product_uom.name, move.product_id.name,\
#                      move.move_id.product_qty, move.move_id.product_uom.name))

                #Adding a check whether any move line contains qty less than zero
                if calc_qty < 0:#EC
                    raise osv.except_osv(_('Processing Error'), \
                            _('Can not process quantity %d for Product %s !') \
                            %(move.quantity, move.product_id.name))

                partial_datas['move%s' % (move.move_id.id)] = {
                    'product_id': move.product_id.id,
                    'product_qty': calc_qty,
                    'product_uom': move.move_id.product_uom.id,
                    'prodlot_id': move.prodlot_id.id,
                }
                if (picking_type == 'in') and (move.product_id.cost_method == 'average'):
                    partial_datas['move%s' % (move.move_id.id)].update({
                                                    'product_price' : move.cost,
                                                    'product_currency': move.currency.id,
                                                    })
        pick_obj.do_partial(cr, uid, picking_ids, partial_datas, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_partial_picking()
