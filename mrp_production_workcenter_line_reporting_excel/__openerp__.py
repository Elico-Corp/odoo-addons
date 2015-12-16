# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Excel report for Mrp Production',
    'version': '8.0.1.0.1',
    'category': 'mrp',
    'depends': [
        'mrp_production_workcenter_line_reporting',
        'report_xls',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'wizard/report_quantity.xml',
        'wizard/report_scraped.xml',
        'report/report_quantity.xml',
        'report/report_scraped.xml',
    ],
    'installable': True,
    'application': False,
}
