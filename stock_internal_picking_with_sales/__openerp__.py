# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Access for Internal Picking with sales',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': 'Separate Internal Picking with sales from normal internal picking',
    'description': """
         Separate internal picking for sales.
         Create a specific menu for it.
    """,
    'depends': ['stock'],
    'category': 'Warehouse Management',
    'sequence': 10,
    'data': [
        'stock_view.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

