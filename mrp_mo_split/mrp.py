# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


from osv import fields, orm
from openerp.tools import float_compare


class mrp_production(orm.Model):
    _inherit = 'mrp.production'

    _columns = {
        'picking_in_id': fields.many2one(
            'stock.picking', 'Picking Finished Goods',
            readonly=True, ondelete="restrict"),
    }
