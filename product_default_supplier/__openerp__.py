# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'product default supplier',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': '',
    'description':
    """
    when create a product, auto create the default supplier info
    """,
    'depends': ['base', 'product'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'company_view.xml',
        'security/ir.model.access.csv',
        ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}


