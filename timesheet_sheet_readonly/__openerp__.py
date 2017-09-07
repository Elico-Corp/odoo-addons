# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Timesheet sheet readonly",
    "summary": "Timesheet Extra",
    "version": "8.0.1.0.0",
    "category": "project",
    "author": "Elico-Corp",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "hr_timesheet_sheet",
    ],
    "data": [
        'views/hr_timesheet_sheet_view.xml',
    ]
}
