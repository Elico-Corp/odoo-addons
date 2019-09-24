# -*- coding: utf-8 -*-
# Copyright 2015-2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Timesheet Activities Report',
    'version': '10.0.1.1.0',
    'category': 'Human Resources',
    'depends': [
        'hr_timesheet',
        'project_issue_sheet',
        'business_requirement_deliverable_project',
        'project_project_category',
        'project_task_category',
    ],
    'author': 'Elico Corp',
    'support': 'support@elico-corp.com',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'security/ir.model.access.csv',
        'report/timesheet_activity_report_view.xml',
    ],
    'installable': True,
    'application': True
}
