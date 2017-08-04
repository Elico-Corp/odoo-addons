# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

import time
from openerp.osv import fields, osv, orm

class sale_order(orm.Model):
    _inherit = "sale.order"
    
    def _prepare_order_picking(self, cr, uid, order, context=None):
        picking_vals = super(sale_order, self)._prepare_order_picking(cr, uid, order, context=context)
        picking_vals['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return picking_vals
