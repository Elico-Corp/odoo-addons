# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Warehouse Management Extend',
    'version': '1.0',
    'category': '',
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    'depends': [
        'stock',
        'mrp'
    ],
    'data': [
        'stock_report.xml',
        'views/report_stockpicking.xml',
        'views/stock.xml',
        'wizard/import_excel_view.xml',
        'stock_view.xml',
        'views/report_stock_lot_barcode.xml',
        'stock_data.xml',
        'wizard/print_product_barcode.xml'
    ],
    'installable': True,
    'application': False,
}
