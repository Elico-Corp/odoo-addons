# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'pos report with total discount',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': 'The POS report should have display the total without discount.',
    'description': """
        * The POS report should have display the total without discount.
        * Add new column totat w/o discouont on point of sale analysis report.
        * Make POS order Salesman mandatory.
    """,
    'depends': ['point_of_sale'],
    'category': 'Sales Management',
    'sequence': 10,
    'data': [
        'point_of_sale_view.xml',
        'report/pos_order_report_view.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}


