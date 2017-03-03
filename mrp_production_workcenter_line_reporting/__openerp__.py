# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Mrp productoin workcenter line reporting',
    'version': '8.0.1.0.1',
    'category': 'mrp',
    'depends': [
        'mrp_operations',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_mrp_workcenter_line_reporting.xml',
        'views/mrp_production_workcenter_line.xml',
        'views/mrp_operations_view.xml',
        'views/mrp_scrapted_reason.xml',
    ],
    'installable': True,
    'application': False,
}
