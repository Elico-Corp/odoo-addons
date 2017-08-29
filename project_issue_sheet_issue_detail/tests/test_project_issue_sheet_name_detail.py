# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TesttestProjectIssueSheetNameDetail(common.TransactionCase):

    def setUp(self):
        super(TesttestProjectIssueSheetNameDetail, self).setUp()
        prod_task = self.env.ref('project.project_task_17')
        crm_bug_id = self.ref('project_issue.crm_case_buginaccountsmodule0')
        project = self.env.ref('project.project_project_1')
        task = project.task_ids.filtered(lambda t: t.name == '%s:%s' %
                                         (project.name, prod_task.name))
        self.line = self.env['account.analytic.line'].create({
                    'name': 'Test Line',
                    'project_id': project.id,
                    'task_id': task.id,
                    'unit_amount': 50,
                    'user_id': 1,
                    'issue_id': crm_bug_id
                })

    def test_name_get(self):
        "Test For name_get method"
        self.line.name_get()
