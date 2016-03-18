# -*- coding: utf-8 -*-
{
    'name': 'Wechat Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Wechat Implementation',
    'version': '8.0.2.0.0',
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
