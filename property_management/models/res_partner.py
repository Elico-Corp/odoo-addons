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
from openerp.osv import osv, fields


class res_partner(osv.Model):
    _inherit = "res.partner"
    
    _columns = {
                'tenant': fields.boolean('Tenant', help="Check this box if this contact is a tenant."),
                'occupation':fields.char('Occupation', size=20),
                'is_tenant':fields.boolean('Tenant', help="Check this box if this contact is a tenant."),
                }

class res_users(osv.Model):
    _inherit = "res.users"
    
    _columns = {
        'tenant_id':fields.many2one('tenant.partner','Related Tenant')
    }