# -*- coding: utf-8 -*-
# © 2011 SYLEAM Info Services (http://www.Syleam.fr)
# © 2011 Sylvain Garancher (sylvain.garancher@syleam.fr)
# © 2011 Sebastien LANGE (sebastien.lange@syleam.fr)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import osv
from openerp.osv import fields


class stock_location_category(osv.osv):
    _name = 'stock.location.category'
    _description = 'Category of stock location'

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of the category of stock location'),
        'code': fields.char('Code', size=64, required=True, help='Code of the category of stock location'),
        'active': fields.boolean('Active', help='This field allows to hide the category without removing it'),
    }

stock_location_category()


class stock_location(osv.osv):
    _inherit = 'stock.location'

    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', help='Warehouse where is located this location'),
        'categ_id': fields.many2one('stock.location.category', 'Category', help='Category of this location'),
    }

stock_location()


