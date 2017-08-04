# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Delivery Time Plan',
    'version': '7.0.1.0.0',
    'category': 'Delivery',
    'sequence': 19,
    'summary': 'Plan delivery time for sale order',
    'description': """
Delivery Time Plan
=================================
* Plan delivery time for sale order
* Add delivery return reason,
* Calculate sale order dts, pts based on order start_date, enddate,
* Compute dts,pts of delivery order based on start_date and end date of sale order, delivery zone of partner.
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['sale_stock', 'delivery_routes',
            'mrp',
            "report_webkit", 'stock_extra'],
    'data': [
        #'security/security.xml',
        'security/ir.model.access.csv',
        'stock_view.xml',
        "delivery_report.xml",
        'wizard/stock_view.xml',
        'sequence.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
