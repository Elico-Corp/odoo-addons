# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Product Stock Type',
    'version': '7.0.1.0.0',
    'category': 'Stock',
    'sequence': 19,
    'summary': 'Add Product Stock Type',
    'description': """
        Product Stock Type
        ==================================================
        * Chinese Language needed - Load Chinese Language
        * Add object Product Stock Type,
        * Add attribute 'deliver in' for product,
        * Add packing sequence in product and stock move,
        * Add name_cn, name_en, name_sort_cn, name_sort_en
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['product', 'stock'],
    'data': [
        'product_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}


