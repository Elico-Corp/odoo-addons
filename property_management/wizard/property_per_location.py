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

from openerp.osv import fields, osv
from openerp.osv import orm, fields, osv

class property_per_location(orm.TransientModel):

    _name = 'property.per.location'
    
    _columns = {
        'state_id': fields.many2one("res.country.state", 'State'),
    }

    def print_report(self, cr, uid, ids, context=None):
      data = self.read(cr, uid, ids[0], context=context)
      return self.pool['report'].get_action(cr, uid, [], 'property_management.report_property_per_location1', data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: