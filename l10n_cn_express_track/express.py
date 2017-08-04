# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.addons.base_status.base_state import base_state
from openerp.osv import fields, osv
from tools.translate import _
from tools import ustr


class res_partner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'is_deliver':  fields.boolean('Deliver?'),
    }
    _defaults = {
        'is_deliver': False,
    }


class stock_picking_express(base_state, osv.Model):
    _name = "stock.picking.express"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Stock Picking Express"
    _order = 'date,deliver_id'

    def _get_url_express(self, cursor, user, ids, name, arg, context=None):
        res = {}
        default_url = "http://www.kuaidi100.com/chaxun?com=%s&nu=%s"
        for express in self.browse(cursor, user, ids, context=context):
            res[express.id] = default_url % (express.deliver_id.ref,
                                             express.num_express)
        return res

    _columns = {
        'deliver_id': fields.many2one(
            'res.partner', 'Deliver Company',
            domain=[('is_deliver', '=', 1)]),
        'state': fields.selection(
            [('draft', 'Draft Quotation'),
             ('cancel', 'Cancelled'),
             ('progress', 'Sales Order'),
             ('manual', 'Sale to Invoice'),
             ('done', 'Done')],
            'Status', readonly=True,
            track_visibility='onchange', select=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'num_express':  fields.char('No. Express'),
        'url_express': fields.function(
            _get_url_express, method=True, type='char',
            string='Link', readonly=1),
        'date': fields.datetime('Date Deliver'),
        'note': fields.text('note'),
    }
