# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author: Ian Li <ian.li@elico-corp.com>
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
    'name': 'Separate Decimal Precision for Invoice Line',
    'version': '0.2',
    'category': 'Finance',
    'description': """
This module corrects the following limitations in OpenERP standard modules:
- In standard accounting module, all objects in the invoice line (unit price, subtotal, etc) are setup following
decimal precision given by 'Account' (eg: 2).

This module introduces a new decimal precision 'Account Line' so that you can have prices in Invoice Line with different accuracy (eg:4)
This means that you can have 2 digits for the invoice total calculation (following your accounting standards) and 4 digits for the invoice details and unit price. 

""",
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn',
    'depends': ['account','decimal_precision'],
    'init_xml': [],
    'update_xml': [
		'data/decimal.precision.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
