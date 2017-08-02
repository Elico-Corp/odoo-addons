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
    'name': 'Enhanced CRM Security Module',
    'version': '1.0',
    'category': 'Sales',
    'description': """
Extension to CRM module to add enhanced security for users 
Objects are:
- meetings
- phonecalls

Default added rules are:
- they can see their own object
- they can see the objects with no user assigned
- they can see their object to the sales teams child of theirs
- they can see the objects with no sales team assigned

    """,
	"author" : "Elico Corp",
    'website': 'http://www.openerp.net.cn',
    'depends': ['crm'],
    'init_xml': [],
    'update_xml': [
		'security/crm_security.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
