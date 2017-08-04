# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    _columns = {
        'container_num': fields.char('Container Number', size=64)
    }


class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'
    _columns = {
        'container_num': fields.char('Container Number', size=64)
    }
