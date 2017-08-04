# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Access Delivery Note Report with Sales Price',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': 'Print Delivery note report with sales price and signature',
    'description': """
         Print Delivery note report with sales price and signature.
         Add Print Delivery Note Button on stock picking.
    """,
    'depends': ['stock', 'report_multi_printout_formats'],
    'category': 'Warehouse Management',
    'sequence': 10,
    'data': [
        'stock_view.xml',
        'stock_report_with_sale_price_report.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}


