# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Timesheet Automatic Reminder',
    'version': '8.0.1.0.0',
    'category': 'Human Resources',
    'depends': [
        'hr_timesheet_sheet',
        'project',
        'hr_holidays_compute_days'
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'data/timesheet_cron_job.xml',
        'data/employee_reminder_template.xml',
        'data/manager_reminder_template.xml'
    ],
    'installable': True,
    'application': False
}
