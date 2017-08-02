# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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


{
    'name': 'Enhanced Partners Security Module',
    'version': '1.0',
    'category': 'Sales',
    'description': """
Extension to Base_contact module to add enhanced security for users 
Objects are:
- partners
- contacts
- Addresses

Default added rules are:
- they can see their own object
- they can see the objects with no user assigned

Added a user_id to res_partner_contact to allow easy filtering for the contacts.

    """,
	"author" : "Elico Corp",
    'website': 'http://www.openerp.net.cn',
    'depends': ['base_contact'],
    'init_xml': [],
    'update_xml': [
		'security/base_security.xml',
        'security/ir.model.access.csv',
		'base_security_view.xml'
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
