# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Timesheet Activities Report',
    'version': '12.0.1.1.0',
    'category': 'Human Resources',
    'depends': [
        'hr_timesheet',
        'helpdesk_timesheet',
        'business_requirement_deliverable_project',
        'project_task_category'
    ],
    'author': 'Elico Corp',
    'support': 'support@elico-corp.com',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'report/timesheet_activity_report_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': False,
    'application': False
}
