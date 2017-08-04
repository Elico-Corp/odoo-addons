# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class stock_warehouse(orm.Model):
    _inherit = 'stock.warehouse'
    _columns = {
        'sale_journal_id': fields.many2one(
            'stock.journal', 'Stock Journal For Sale')
    }


class stock_journal(orm.Model):
    _inherit = 'stock.journal'
    _columns = {
        'warehouse_ids': fields.one2many(
            'stock.warehouse', 'sale_journal_id', 'Warehouses')
    }


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context)
        warehouse_id = order.shop_id and order.shop_id.warehouse_id
        if warehouse_id:
            res['stock_journal_id'] = warehouse_id.sale_journal_id and\
                warehouse_id.sale_journal_id.id
        return res
