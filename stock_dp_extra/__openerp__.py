# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Stock Decimal Precision Extra',
    'version': '7.0.1.0.0',
    'category': 'Warehouse',
    'description': """
This module corrects the following limitations in OpenERP standard modules:
- In stock module, standard cost in stock move is defined following 'Account' decimal precision.

This module introduces a new decimal precision 'Stock Move' so that you can have standard cost different accuracy (eg:4) than the accounting.
This means that you can have 2 digits for the accounting and 4 digits for the stock move. 
""",
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['decimal_precision', 'stock'],
    'update_xml': [
		'data/decimal.precision.xml',
	],
    'installable': True,
    'active': False,
}
