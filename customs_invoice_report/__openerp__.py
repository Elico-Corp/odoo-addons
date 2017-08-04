# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Custom Invoice Report',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'description': """
         customs_invoice_report
         
          invoice tree view, 'more' button, 'Customs Invoice Report',
    """,
    'depends': ['base', 'account'],
    'category': '',
    'sequence': 10,
    'data': [
        'wizard/wizard_customs_invoice_report.xml',
        'report/customs_invoice_report.xml',
       
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}


