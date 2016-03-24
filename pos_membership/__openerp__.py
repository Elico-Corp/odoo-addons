# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Membership Management - POS Membership',
    'version': '8.0.1.0.1',
    'category': 'Generic Modules',
    'depends': [
        'membership_account_balance',
        'point_of_sale',
        'account_accountant',
        'account_voucher',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'views/pos_membership.xml',
        'views/partner_view.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'installable': True,
    'application': False,
}
