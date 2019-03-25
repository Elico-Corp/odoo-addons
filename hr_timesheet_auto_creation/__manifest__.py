# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR TimeSheet Auto Creation",
    "summary": """
Automatic Timesheet will add a cron job for create the time sheet.
    """,
    "version": "10.0.1.0.0",
    "category": "Human Resources",
    "author": "Elico Corp",
    "license": "AGPL-3",
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    "depends": [
        "hr_timesheet_sheet",
    ],
    "data": [
        "data/hr_timesheet_sheet_cron_job.xml",
    ],
    "application": True,
    "installable": True,
}
