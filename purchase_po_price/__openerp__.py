# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Purchase PO Price',
    'version': '7.0.1.0.0',
    'category': 'Purchase',
    'sequence': 19,
    'summary': 'Purchase PO Price',
    'description': """ Enable/Disable control on PO Price """,
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