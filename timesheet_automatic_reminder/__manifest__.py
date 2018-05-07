# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Timesheet Automatic Reminder',
    'version': '10.0.1.1.0',
    'category': 'Human Resources',
    'depends': [
        'hr_timesheet_sheet',
        'project',
        'hr_holidays'
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    'data': [
        'data/timesheet_cron_job.xml',
        'data/employee_reminder_template.xml',
        'data/manager_reminder_template.xml'
    ],
    'installable': True,
}
