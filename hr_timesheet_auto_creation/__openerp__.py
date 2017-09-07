# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR TimeSheet auto creation",
    "summary": """
Automatic Timesheet will add a cron job for create the time sheet.
    """,
    "version": "8.0.1.0.0",
    "category": "Human Resources",
    "author": "Elico Corp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "hr_timesheet_sheet",
    ],
    "data": [
        "data/hr_timesheet_sheet_cron_job.xml",
    ]
}
