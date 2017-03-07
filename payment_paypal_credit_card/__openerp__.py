# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Paypal Credit card Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Paypal Credit card Implementation',
    'version': '8.0.1.0.0',
    'author': 'Elico Corp, OpenERP SA',
    'depends': ['payment_paypal', 'website_sale'],
    'support': 'support@elico-corp.com',
    'data': [
        'payment_view.xml',
        'data/payment.xml',
        'views/templates.xml'
    ],
    'installable': True,
}
