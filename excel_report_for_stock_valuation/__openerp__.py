# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Excel report for stock valutaion',
    'version': '8.0.1.0.1',
    'depends': [
        'stock_account',
        'report_xls',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'report/report.xml',
        'wizard/report_stock_list.xml',
        'wizard/report_stock.xml',
    ],
    'installable': True,
    'application': False,
}
