# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com)
# Elico Proprietary License v1.0.
# See LICENSE file for full copyright and licensing details.
from odoo.tests import common


class TestProjectTaskSave(common.TransactionCase):

    def setUp(self):
        super(TestProjectTaskSave, self).setUp()
        self.name_1 = self.env.ref('project.project_task_9')
        self.name_2 = self.env.ref('project.project_task_8')
        self.project_id = self.env.ref('project.project_project_4')
        self.user_id = self.env.ref('base.user_root')
        self.sub_extra_time = 0
        self.timesheet_ids = self.env['account.analytic.line'].write([[
            0, False, {
                'date_time': '2017-12-15',
                'user_id': self.user_id.id,
                'name': 'test',
                'unit_amount': 1,
                'date': '2017-12-15',
                'project_id': self.project_id.id
            }
        ]])
        self.task_1 = self.env['project.task'].create({
            'name': self.name_1.id,
            'project_id': self.project_id.id,
            'user_id': self.user_id.id,
            'planned_hours': 18,
            'remaining_hours': 18,
            'timesheet_ids': self.timesheet_ids
        })
        self.task_2 = self.env['project.task'].create({
            'name': self.name_2.id,
            'project_id': self.project_id.id,
            'user_id': self.user_id.id,
            'planned_hours': 18,
            'remaining_hours': 1,
            'timesheet_ids': self.timesheet_ids
        })
        self.view_id = self.env.ref(
            'extra_time_application.project_task_form_inherit_view').id

    def test_save(self):
        vals_1 = {'remaining_hours': 23}
        self.task_1.write(vals_1)
        vals_2 = {'timesheet_ids': [[4, 20, False], [0, False, {
            'date_time': '2017-12-13 10:26:54',
            'user_id': 1,
            'name': self.name_2,
            'unit_amount': 2,
            'date': '2017-12-13',
            'project_id': self.project_id.id
        }]]}
        self.task_1.write(vals_2)
        try:
            self.task_2.write(vals_2)
        except Exception:
            pass

    def test_open_extra_time_line(self):
        self.task_1.open_extra_time_line()

    def test_fields_view_get(self):
        self.task_1.fields_view_get(view_id=self.view_id, view_type='form')
