# -*- coding: utf-8 -*-
# © 2018 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common


class TestProjectProjectCategory(common.TransactionCase):

    def test_create(self):
        self.env["project.project.category"].create({
            'name': "Support Projects",
        })
