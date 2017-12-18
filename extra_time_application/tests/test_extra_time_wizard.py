# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com)
# Elico Proprietary License v1.0.
# See LICENSE file for full copyright and licensing details.
from odoo.tests import common


class TestExtraTimeWizard(common.TransactionCase):

    def setUp(self):
        super(TestExtraTimeWizard, self).setUp()
        self.task_id = self.env.ref('project.project_task_9')
        self.submit_user_id = self.env.ref('base.user_demo')
        self.extra_time_1 = self.env['extra.time.application.wizard'].create({
            'submit_user_id': self.submit_user_id.id,
            'task_id': self.task_id.id,
            'reason': 'system test',
            'apply_hours': 3
        })
        self.extra_time_2 = self.env['extra.time.application.wizard'].create({
            'submit_user_id': self.submit_user_id.id,
            'task_id': self.task_id.id,
            'reason': 'system test',
            'apply_hours': 3
        })

    def test_subscribe(self):
        self.extra_time_1.subscribe()
        self.extra_time_2.subscribe()
