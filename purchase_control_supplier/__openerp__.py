# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Purchase Control Supplier',
    'version': '7.0.1.0.0',
    'category': 'Purchase',
    'sequence': 19,
    'summary': 'Purchase Control Supplier',
    'description': """
        Enables/Disables the supplier control in Purchase.
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['purchase'],
    'data': [
        'purchase_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

