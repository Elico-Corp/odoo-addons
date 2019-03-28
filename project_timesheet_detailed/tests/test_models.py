# -*- coding:utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from odoo.exceptions import UserError


class TestTimesheetDetail(common.TransactionCase):

    def setUp(self):
        super(TestTimesheetDetail, self).setUp()
        self.account = self.env.ref('analytic.analytic_millennium_industries')
        self.task_1 = self.env.ref('project.project_task_1')
        self.task_2 = self.env.ref('project.project_task_20')
        self.issue_1 = self.env.ref(
            'project_issue.crm_case_buginaccountsmodule0')
        self.issue_2 = self.env.ref(
            'project_issue.crm_case_programnotgivingproperoutput0')
        self.timesheet_1 = self.env['account.analytic.line'].create({
            'name': 'test timesheet',
            'task_id': self.task_1.id,
            'date': '2018-1-10',
            'unit_amount': 2,
            'stage': 'to review',
            'account_id': self.account.id
        })
        self.timesheet_2 = self.env['account.analytic.line'].create({
            'name': 'test test timesheet',
            'task_id': self.task_2.id,
            'date': '2018-1-10',
            'unit_amount': 2,
            'stage': 'to review',
            'account_id': self.account.id
        })
        self.timesheet_3 = self.env['account.analytic.line'].create({
            'name': 'test timesheet',
            'issue_id': self.issue_1.id,
            'date': '2018-1-10',
            'unit_amount': 2,
            'stage': 'approved',
            'account_id': self.account.id
        })
        try:
            self.env['account.analytic.line'].create({
                'name': 'test timesheet',
                'issue_id': self.issue_1.id,
                'task_id': self.task_1.id,
                'date': '2018-1-10',
                'unit_amount': 2,
                'stage': 'to review',
                'account_id': self.account.id
            })
        except ValueError:
            pass

    def test_set_approved(self):
        try:
            self.timesheet_1.set_approved()
            self.timesheet_2.set_approved()
        except UserError as e:
            self.assertEquals(e.name,
                              'Sorry,you do not have permission to approve it')

    def test_set_rejected(self):
        try:
            self.timesheet_1.set_rejected()
            self.timesheet_2.set_rejected()
        except UserError as e:
            self.assertEquals(e.name,
                              'Sorry,you do not have permission to reject it')

    def test_set_review(self):
        try:
            self.timesheet_1.set_review()
            self.timesheet_2.set_review()
        except UserError as e:
            self.assertEquals(
                e.name, 'Sorry,you do not have permission to change the state')

    def test_onchange_project_id(self):
        self.timesheet_1.task_id = self.task_2.id
        self.assertEquals(self.timesheet_1.project_id, self.task_2.project_id)

    def test_issue_id_on_change(self):
        self.timesheet_3.issue_id = self.issue_2.id
        self.assertEquals(self.timesheet_3.project_id, self.issue_2.project_id)

    def test_write(self):
        vals_1 = {'task_id': self.task_2.id}
        self.timesheet_1.write(vals_1)
        self.assertEquals(self.timesheet_1.project_id, self.task_2.project_id)

    def test_unlink(self):
        try:
            self.timesheet_3.unlink()
        except UserError as e:
            self.assertEquals(e.name,
                              'Only records in to review can be deleted!')
