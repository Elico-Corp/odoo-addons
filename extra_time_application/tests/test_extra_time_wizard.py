# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com)
# Elico Proprietary License v1.0.
# See LICENSE file for full copyright and licensing details.
from odoo.tests import common


class TestExtraTimeWizard(common.TransactionCase):

    def setUp(self):
        super(TestExtraTimeWizard, self).setUp()
        self.task_no = self.env.ref('project_task_1')
        self.submit_user_id = self.env.ref('base.user_demo')
        self.extra_time_1 = self.env['extra.time.application'].create({
            'submit_user_id': self.submit_user_id,
            'task_no': self.task_no,
            'reason': 'system test',
            'apply_hours': 3
        })
        self.extra_time_2 = self.env['extra.time.application'].create({
            'submit_user_id': self.env.ref('base.res.partner'),
            'task_no': self.task_no,
            'reason': 'system test',
            'apply_hours': 3
        })

        def test_subscribe():
            self.extra_time_1.subscribe()
            self.extra_time_2.subscribe()
