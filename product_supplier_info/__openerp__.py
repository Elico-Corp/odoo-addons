# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Product Supplier Info',
    'version': '7.0.1.0.0',
    'category': 'purchase',
    'sequence': 19,
    'summary': 'Product Supplier Info',
    'description': """
        Add a specific View for Supplier 
        ==================================================
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['product','stock'],#TO REMOVE joomlaconnector for standard
    'data': [
        'product_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

