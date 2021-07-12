# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Project Completion Report",
    "summary": "Follow-up project completion (estimated / consumed)",
    "version": "12.0.1.0.0",
    "category": "Project",
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    "author": "Elico Corp",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_timesheet",
        "helpdesk_timesheet",
        "project_project_category",
        "business_requirement_deliverable_project",
    ],
    "data": [
        "report/project_completion_report_view.xml",
        "security/ir.model.access.csv",
    ],
}
