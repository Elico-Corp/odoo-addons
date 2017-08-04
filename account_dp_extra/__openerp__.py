# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)



{
    'name': 'Separate Decimal Precision for Invoice Line',
    'version': '7.0.1.0.0',
    'category': 'Finance',
    'description': """
This module corrects the following limitations in OpenERP standard modules:
- In standard accounting module, all objects in the invoice line (unit price, subtotal, etc) are setup following
decimal precision given by 'Account' (eg: 2).

This module introduces a new decimal precision 'Account Line' so that you can have prices in Invoice Line with different accuracy (eg:4)
This means that you can have 2 digits for the invoice total calculation (following your accounting standards) and 4 digits for the invoice details and unit price. 

""",
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['account','decimal_precision'],
    'update_xml': [
		'data/decimal.precision.xml',
	],
    'installable': True,
    'active': False,
}
