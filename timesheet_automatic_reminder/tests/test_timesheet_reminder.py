# -*- coding: utf-8 -*-
# © 2018 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from odoo.tests import common


class TestTimesheetReminder(common.TransactionCase):

    def setUp(self):
        super(TestTimesheetReminder, self).setUp()
        self.reminder_line = self.env['reminder.date.line'].create({
            'reminder_date': datetime.date.today(),
            'reminder_id.employee_id': 1,
        })
        self.timesheet_line = self.env['timesheet.reminder'].create({
            'work_on_time': datetime.datetime(2018, 05, 04, 10, 15, 15),
            'work_off_time': datetime.datetime(2018, 05, 04, 18, 30, 15),
            'rest_hours': 1.00,
        })

    def test_check_is_working_day(self):
        self.reminder_line._check_is_working_day()

    def test_get_leave_hours(self):
        self.reminder_line._get_leave_hours()

    def test_get_work_hours(self):
        self.reminder_line._get_work_hours()

    def test_get_work_hours_1(self):
        self.timesheet_line._get_work_hours()

    def test_start_reminder(self):
        self.timesheet_line._start_reminder(5, '08:00:00', '18:00:00', 1)

    def test_start_reminder_2(self):
        self.timesheet_line._start_reminder(5, '08:00:00', '18:00:00', 1,
                                            reminder_type=2)
