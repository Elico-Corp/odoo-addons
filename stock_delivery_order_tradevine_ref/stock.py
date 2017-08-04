# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    _columns = {
        'client_order_ref': fields.char(
            'Tradevine Ref',
            states={'done': [('readonly', True)],
                    'cancel': [('readonly', True)]},
            help="Reference of the document", size=61, select=True)
    }


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'
    _columns = {
        'client_order_ref': fields.char(
            'Tradevine Ref',
            states={'done': [('readonly', True)],
                    'cancel': [('readonly', True)]},
            help="Reference of the document", size=61, select=True)
    }


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context)
        res['client_order_ref'] = order.client_order_ref
        return res


class stock_move(orm.Model):
    _inherit = "stock.move"

    def _prepare_chained_picking(
        self, cr, uid, picking_name, picking,
            picking_type, moves_todo, context=None):
        """Prepare the definition (values) to create a new chained picking.

           :param str picking_name: desired new picking name
           :param browse_record picking: source picking (being chained to)
           :param str picking_type: desired new picking type
           :param list moves_todo: specification of the stock moves to be later
            included in this
               picking, in the form::

                   [[move, (dest_location, auto_packing, chained_delay,
                    chained_journal,
                                  chained_company_id, chained_picking_type)],
                    ...
                   ]

               See also :meth:`stock_location.chained_location_get`.
        # rewrite this method just wanna pass the custom field client_order_ref
        """
        res = super(stock_move, self)._prepare_chained_picking(
            cr, uid, picking_name, picking, picking_type, moves_todo, context)
        res['client_order_ref'] = picking and picking.client_order_ref
        return res
