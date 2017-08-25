# -*- coding: utf-8 -*-
# © 2017 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.tests import common


class TestProjectPartnerName(common.TransactionCase):

    def setUp(self):
        super(TestProjectPartnerName, self).setUp()
        self.project_obj = self.env['project.project']
        self.analytic_acc_obj = self.env['account.analytic.account']
        self.project1 = self.env.ref('project.project_project_3')
        self.partner1 = self.env.ref('base.res_partner_2')
        self.partner1.ref = 'ref1'
        self.project2 = self.env.ref('project.project_project_5')
        self.partner2 = self.env.ref('base.res_partner_address_13')
        self.partner2.parent_id.ref = 'ref2'

    def test_name_get_search(self):
        """Check namge_get and namge_search of Project / Analytic
        Partner Name Ref"""
        proj_name1 = self.project1.name
        self.assertEqual(self.project1.name_get()[0][1],
                         self.partner1.ref + ' - ' + proj_name1)
        self.assertEqual(self.project2.name_get()[0][1],
                         self.partner2.parent_id.ref + ' - ' +
                         self.project2.name)
        self.assertEqual(self.project_obj.name_search(proj_name1)[0][1],
                         self.partner1.ref + ' - ' + proj_name1)
        analytic_name = self.analytic_acc_obj.name_search(
            self.project1.analytic_account_id.name
        )
        self.assertEqual(analytic_name[0][1],
                         self.partner1.ref + ' - ' + proj_name1)
