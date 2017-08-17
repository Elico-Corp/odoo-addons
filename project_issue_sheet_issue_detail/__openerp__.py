# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Issue Sheet Issue Detail",
    "summary": """
This module extends the functionality when a user creates an issue,
he/she can see the issue ID on the time sheet description in table details.
    """,
    "version": "8.0.1.0.0",
    "category": "project",
    "author": "Elico Corp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "project_issue_sheet",
    ],
    "data": [
        "hr_timesheet_sheet_view.xml",
    ]
}
