# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

from datetime import datetime, timedelta


class TestHrTimesheetSheet(common.TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheet, self).setUp()
        self.tms_obj = self.env['hr_timesheet_sheet.sheet']
        today = datetime.now()
        self.monday = today + timedelta(days=-today.weekday())
        self.sunday = self.monday + timedelta(days=+6)

        self.user1 = self.env.ref('base.user_root').copy({'login': 'test1'})
        self.employee1 = self.env.ref('hr.employee_ngh')
        self.employee1.user_id = self.user1.id
        self._create_timesheet_sheet(self.employee1.id)

        self.user2 = self.user1.copy({'login': 'test2'})
        self.employee2 = self.env.ref('hr.employee_vad').copy({
            'user_id': self.user2.id,
        })

    def _create_timesheet_sheet(self, employee_id):
        self.tms_obj.sudo().create({
            'name': 'TMS - 1',
            'employee_id': employee_id,
            'date_from': self.monday.strftime('%Y-%m-%d'),
            'date_to': self.sunday.strftime('%Y-%m-%d'),
        })

    def test_create_employee_timesheet(self):
        """Check timesheet has been created automatically for the week."""
        self.tms_obj.create_employee_timesheet()
        tms = self.tms_obj.search([('employee_id', '=', self.employee2.id),
                                   ('date_to', '>=', self.monday),
                                   ('date_to', '<=', self.sunday)], limit=1)
        self.assertEqual(tms.employee_id, self.employee2)
