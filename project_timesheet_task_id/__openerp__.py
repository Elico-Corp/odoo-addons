# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Timesheet Task Detail",
    "summary": """
This module will change the description of task.
    """,
    "version": "8.0.1.0.0",
    "category": "project",
    "author": "Elico Corp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "project_timesheet",
    ],
    "data": [
        "project_timesheet_task_id_view.xml",
    ],
}
