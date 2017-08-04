# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Stock With Cost',
    'version': '7.0.1.0.0',
    'category': 'Stock',
    'sequence': 19,
    'summary': 'Stock with Cost',
    'description': """
        Stock With Cost
        ==================================================
        * Add Cost (POL Price) in Stock Move, Stock picking
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['stock_extra'],
    'data': [
        'stock_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}


