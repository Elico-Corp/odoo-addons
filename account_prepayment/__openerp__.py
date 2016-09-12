# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Prepayment',
    'version': '8.0.1.0.1',
    'category': 'Account',
    'summary': 'Account Prepayment',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'depends': [
        'account',
        'account_voucher',
        'purchase'
    ],
    'data': [
        'views/account_view.xml',
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 20,
}
