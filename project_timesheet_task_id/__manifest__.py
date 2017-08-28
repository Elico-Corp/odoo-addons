# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Timesheet Task Detail",
    "summary": """
This module will change the description of task.
    """,
    "version": "10.0.1.0.0",
    "category": "project",
    "author": "Elico Corp",
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet",
    ],
    "data": [
        "views/project_timesheet_task_id_view.xml",
    ],
    "installable": True,
}
