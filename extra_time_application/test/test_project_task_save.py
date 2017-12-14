# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com)
# Elico Proprietary License v1.0.
# See LICENSE file for full copyright and licensing details.
from odoo.tests import common


class TestProjectTaskSave(common.TransactionCase):

    def setUp(self):
        super(TestProjectTaskSave, self).setUp()
        self.name = self.env.ref('project.project_task_9')
        self.project_id = self.env.ref('project.project_project_2')
        self.user_id = self.env.ref('base.user_demo')
        self.sub_extra_time = 0
        self.task_1 = self.env['project.task'].create({
            'name': self.name,
            'project_id': self.project_id,
            'user_id': self.user_id.id,
            'planned_hours': 18,
            'remaining_hours': 18,
            'timesheet_ids':
            [(0, 0, {
                'date': '2017-12-13',
                'name': 'test',
                'unit_amount': 2,
            })]
        })
        self.task_2 = self.env['project.task'].create({
            'name': self.name,
            'project_id': self.project_id,
            'user_id': self.user_id.id,
            'planned_hours': 18,
            'remaining_hours': -1,
            'timesheet_ids':
                [(0, 0, {
                    'date': '2017-12-13',
                    'name': 'test',
                    'unit_amount': 2,
                })]
        })
        self.view_id = self.env.ref('project_task_form_inherit_view').id

    def test_save(self):
        vals_1 = {'remaining_hours':23}
        self.task_1.write(vals_1)
        vals_2 = {'timesheet_ids':[[4,20,False],[0,False,{
            'date_time': '2017-12-13 10:26:54',
            'user_id':  1,
            'name': self.name,
            'unit_amount': 2,
            'date': '2017-12-13',
            'project_id': self.project_id
        }]]}
        self.task_1.write(vals_2)
        self.task_2.write()

    def test_open_extra_time_line(self):
        res = self.task_1.open_extra_time_line()
        self.assertTrue(res[1], 'error')
        return res

    def test_fields_view_get(self):
        self.task_1.fields_view_get(view_id=self.view_id,
                                           view_type='form')


