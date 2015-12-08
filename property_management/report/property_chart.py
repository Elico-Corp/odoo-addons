# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
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
############################################################################

from openerp import tools
from openerp.osv import fields, osv

class property_finance_report(osv.osv):
    _name = "property.finance.report"
    _auto = False


    _columns = {
        'type_id':fields.many2one('property.type', 'Property Type'),
        'purchase_date':fields.date('Purchase Date'),
        'parent_id':fields.many2one('account.asset.asset', 'Parent Property'),
        'name':fields.char("Parent Property"),
        'purchase_price':fields.float('Purchase Price'),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        obj = cr.execute("""CREATE or REPLACE VIEW property_chart_report as SELECT id,name,type_id,purchase_price,purchase_date
            FROM account_asset_asset""" )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: