# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Timesheet Activities Report',
    'version': '8.0.1.1.0',
    'category': 'Human Resources',
    'depends': [
        'project_timesheet',
        'project_issue_sheet',
        'business_requirement',
        'business_requirement_deliverable_project',
        'project_task_category'
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'report/timesheet_activity_report_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False
}
