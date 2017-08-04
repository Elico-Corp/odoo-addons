# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class stock_warehouse(orm.Model):
    _inherit = 'stock.warehouse'
    _columns = {
        'purchase_journal_id': fields.many2one(
            'stock.journal', 'Stock Journal For Purchase')
    }


class stock_journal(orm.Model):
    _inherit = 'stock.journal'
    _columns = {

    }


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(purchase_order, self)._prepare_order_picking(
            cr, uid, order, context)
        if order.warehouse_id:
            res['stock_journal_id'] = order.warehouse_id.purchase_journal_id\
                and order.warehouse_id.purchase_journal_id.id
        return res
