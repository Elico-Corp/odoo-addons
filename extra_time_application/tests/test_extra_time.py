# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from odoo.exceptions import UserError


class TestExtraTime(common.TransactionCase):

    def setUp(self):
        super(TestExtraTime, self).setUp()
        self.submit_user_id = self.env.ref("base.user_demo")
        self.task_id = self.env.ref('project.project_task_9')

        self.extra_time_record = self.env['extra.time.application'].create({
            'submit_user_id': self.submit_user_id.id,
            'task_id': self.task_id.id,
            'reason': 'Automatically created From PM or Reviewer',
            'apply_hours': 2,
            'state': 'to_approve'
        })

    def test_approve_function(self):
        try:
            self.extra_time_record.approve_function()
        except UserError:
            pass


    def test_refuse_function(self):
        try:
            self.extra_time_record.refuse_function()
        except UserError:
            pass

