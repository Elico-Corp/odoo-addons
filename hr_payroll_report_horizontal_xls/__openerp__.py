# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Hr Payroll Horizontal Xls Report',
    'version': '8.0.1.0.1',
    'category': 'hr',
    'depends': [
        'hr_payroll',
        'report_xls',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'hr_payroll_report_horizontal_xls_view.xml',
        'report_hr_payroll.xml',
    ],
    'installable': True,
    'application': False,
}
