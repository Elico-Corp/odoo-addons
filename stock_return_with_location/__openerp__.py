# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Return location',
    'version': '7.0.1.0.0',
    'category': 'Stock',
    'sequence': 20,
    'summary': 'Return product to specified location',
    'description': """
Return with location
==================================================
When you return a product, you can specify a warehouse location you want.
Fixed: Sequence is not created for return internal picking, partial internal picking and back order of internal picking
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['stock'],
    'data': [
        'stock_return_with_location_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

