# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Account Alternate Invoice',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'description': """
         Account Alternate Invoice
    """,
    'depends': ['base', 'account', ],
    'sequence': 10,
    'data': [
        'account_invoice_view.xml',
        'report.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}


