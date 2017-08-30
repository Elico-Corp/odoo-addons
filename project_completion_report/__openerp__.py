# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Completion Report",
    "summary": "Follow-up project completion (estimated / consumed)",
    "version": "8.0.1.0.2",
    "category": "Project",
    "website": "https://odoo-community.org/",
    "author": "Sebastien Maillard, Elico Corp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project_timesheet",
        "project_issue_sheet",
        "project_project_category",
        "business_requirement_deliverable_project",
    ],
    "data": [
        "report/project_completion_report_view.xml",
        "security/ir.model.access.csv",
    ],
}

