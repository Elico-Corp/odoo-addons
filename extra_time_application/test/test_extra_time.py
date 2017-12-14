# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com)
# Elico Proprietary License v1.0.
# See LICENSE file for full copyright and licensing details.
from odoo.tests import common


class TestExtraTime(common.TransactionCase):

    def setUp(self):
        super(TestExtraTime, self).setUp()
        self.submit_user_id = self.env.ref("base.partner_root")
        self.task_no = self.env.ref('project.project_task_9')

        self.extra_time_record = self.env['extra.time.application'].create({
            'submit_user_id': self.submit_user_id,
            'task_no': self.task_no,
            'reason': 'Automaticity create From PM or Reviewer',
            'apply_hours': 2,
            'state': 'to_approve'
        })

    def test_approve_function(self):
        self.extra_time_record.approve_function()

    def test_refuse_function(self):
        self.extra_time_record.refuse_function()
