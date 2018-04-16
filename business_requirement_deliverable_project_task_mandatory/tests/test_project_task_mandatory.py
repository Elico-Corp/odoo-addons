# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common

class TestProjectMandatory(common.TransactionCase):

    def setUp(self):
        super(TestProjectMandatory,self).setUp()
        Task1 = self.env.ref('project.project_task_3')
        project1 = self.env.ref('project.project_project_1')
        business_requirement_id1 = self.env.ref('business_requirement_deliverable.business_requirement_id')
        self.demo=self.env['project.task'].write({
            'project_id': project1.id,
            'business_requirement_id': business_requirement_id1,
            'br_required': True

        })

    def test_report(self):
        try:
            self.demo._check_br_required()
        except Exception as e:
            pass




