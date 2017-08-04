# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'sale payment prepayment',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': '',
    'description': """
         sale payment prepayment
    """,
    'depends': ['base', 'account_prepayment', 'sale_payment_method', ],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'sale_payment_prepayment_view.xml',
        # 'security/ir.model.access.csv',
        ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}


