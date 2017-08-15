# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock Valuation Xls Report',
    'summary': 'Stock Valuation Xls Report',
    'version': '9.0.1.0.1',
    'website': 'https://www.elico-corp.com',
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    "application": False,
    'installable': True,
    'depends': [
        'mrp',
        'purchase',
        'report_xls',
        'sale',
        'stock_account',
    ],
    'data': [
        'report/report_stock_valuation.xml',
        'wizard/wizard_stock_list.xml',
        'wizard/wizard_stock.xml',
    ],
}
