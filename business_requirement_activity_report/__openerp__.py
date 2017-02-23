# -*- coding: utf-8 -*-
#   2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
<<<<<<< HEAD:timesheet_activity_report/__openerp__.py
    'name': 'Timesheet Activities Report',
    'version': '8.0.1.0.3',
=======
    'name': 'Business Requirement Activity Report',
    'version': '8.0.1.2.0',
>>>>>>> 7d50dc810f507665195ddc012a1b152c55ffe6e5:business_requirement_activity_report/__openerp__.py
    'category': 'Human Resources',
    'depends': [
        'project_timesheet',
        'project_issue_sheet',
<<<<<<< HEAD:timesheet_activity_report/__openerp__.py
        'business_requirement',
        'business_requirement_deliverable_project'
=======
        'project_task_category',
        'project_project_category',
        'business_requirement'
>>>>>>> 7d50dc810f507665195ddc012a1b152c55ffe6e5:business_requirement_activity_report/__openerp__.py
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'images': [],
    'data': [
        'report/timesheet_activity_report_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False
}
