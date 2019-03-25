# -*- coding: utf-8 -*-
# © 2018 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestProjectTask(common.TransactionCase):

    def setUp(self):
        super(TestProjectTask, self).setUp()
        self.project_id = self.env.ref('project.project_project_1')
        self.business_requirement_id = self.env.ref(
            'business_requirement.business_requirement_4')
        self.project_line = self.env["project.task"].create({
            'name': 'task_1',
            'project_id': self.project_id.id,
            'business_requirement_id': self.business_requirement_id.id,
        })

    def test_check_br_required(self):
        self.project_line._check_br_required()
