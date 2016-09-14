# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Prepayment',
    'version': '8.0.1.0.1',
    'category': 'Account',
    'summary': '''Prepayment Account for customers and usage of prepayment
        account for payments in purchase''',
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
    'images': [
        'static/description/account_invoice_line1.png',
        'static/description/account_invoice_line2.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 20,
}
