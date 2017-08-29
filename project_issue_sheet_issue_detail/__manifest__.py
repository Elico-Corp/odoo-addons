# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Issue Sheet Issue Detail",
    "summary": """This module extends the functionality when a user creates an
    issue, he/she can see the issue ID on the time sheet description in table
    details.""",
    'version': '10.0.1.0.0',
    "category": "project",
    "author": "Elico Corp",
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    "license": "AGPL-3",
    "depends": [
        "project_issue_sheet",
    ],
    "data": [
        "views/hr_timesheet_sheet_view.xml",
    ],
    "installable": True,
}
