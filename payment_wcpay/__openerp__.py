# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Wechat Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Wechat Implementation',
    'version': '9.0.2.0.0',
    'website': 'www.elico-corp.com',
    "author": "Elico Corp",
    'depends': [
        'website_sale',
    ],
    'external_dependencies': {
        'python': ['cgi']
    },
    'data': [
        'views/wcpay_view.xml',
        'views/payment_acquirer.xml',
        'data/wcpay.xml',
    ],
    'installable': True,
}
