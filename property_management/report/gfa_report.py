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

from openerp import tools
from openerp.osv import fields, osv

class property_report(osv.osv):
    _name = "property.report"
    _auto = False

    _columns = {
        'type_id':fields.many2one('property.type', 'Property Type'),
        'gfa_feet':fields.float('GFA(Sqft)'),
        'purchase_date':fields.date('Purchase Date'),
        'name': fields.char('Asset Name')
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        obj = cr.execute("""CREATE or REPLACE VIEW property_report as SELECT id,name,type_id,gfa_feet,purchase_date
            FROM account_asset_asset""" )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
