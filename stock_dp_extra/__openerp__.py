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
    'name': 'Separate Decimal Precision for stock moves',
    'version': '0.2',
    'category': 'Warehouse',
    'description': """
This module corrects the following limitations in OpenERP standard modules:
- In stock module, standard cost in stock move is defined following 'Account' decimal precision.

This module introduces a new decimal precision 'Stock Move' so that you can have standard cost different accuracy (eg:4) than the accounting.
This means that you can have 2 digits for the accounting and 4 digits for the stock move. 
""",
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn',
    'depends': ['decimal_precision', 'stock'],
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
