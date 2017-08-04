# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Product Price Category',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'description' : """
     Display the price category for products.
    """,
    'depends': ['base','product', 'sale','purchase'],
    'sequence': 16,
    'data': [      
        'price_category.xml',
        'security/ir.model.access.csv',
        'pricelist.xml',
        'product_view.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,

}



