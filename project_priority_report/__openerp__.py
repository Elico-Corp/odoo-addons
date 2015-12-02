# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project Priority Report',
    'version': '8.0.1.0.1',
    'category': 'Human Resources',
    'depends': [
        'hr_timesheet',
        'project_timesheet',
        'project_issue_sheet',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'report/project_priority_report_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
