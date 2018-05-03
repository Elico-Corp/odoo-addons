# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Invoice Report',
    'version': '10.0.1.0.1',
    'category': '',
    'depends': ['stock', 'sale'],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    'data': [
        # 'invoice_report.xml',
        'views/report_saleorder_extend.xml',
        'views/report_invoice_extend.xml',
        'views/report_stockpicking_extend.xml',
        'views/report_stockpicking_extend_full.xml',
        'views/invoice_report.xml',
        'views/report_draft_order_invoice.xml',
        # 'company_view.xml'
    ],
    'installable': True,
}
