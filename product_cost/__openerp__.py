# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'product cost',
    'version': '8.0.1.0.1',
    'category': 'manufacture',
    'depends': [
        'report_xls',
        'mrp',
        'account',
    ],
    'external_dependencies': {
        'python': ['xlrd'],
    },
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    "support": "support@elico-corp.com",
    'data': [
        'wizard/product_cost_import.xml',
        'security/ir.model.access.csv',
        'product_cost_view.xml',
    ],
    'installable': True,
    'application': False,
}
