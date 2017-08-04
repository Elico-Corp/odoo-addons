# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'sales_man': fields.many2one(
            'res.users', 'Source product', ondelete='cascade'),
    }

class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'sales_man': fields.many2one(
            'res.users', 'Portal Sales', ondelete='cascade'),
    }


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_order_picking(self, cr, uid, order, context=None):
        picking_vals = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        picking_vals['sales_man'] = order.user_id and order.user_id.id or False
        return picking_vals
