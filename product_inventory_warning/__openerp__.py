# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Product Inventory Warning',
    'version': '7.0.1.0.0',
    'category': 'Product',
    'sequence': 1,
    'summary': 'Product Inventory Warning',
    'description': """
        Product Inventory Warning
        ==================================================

        Add a wizard to calculate the QTY of product.
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['product', 'product_stock_type','product_separate_cost','stock_with_cost'],
    'data': [
        'product_view.xml',
        'wizard/product_qty_view.xml',
        'wizard/product_sfc_view.xml',
        'security/ir.model.access.csv',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}


