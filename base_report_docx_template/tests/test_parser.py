# -*- coding: utf-8 -*-

from openerp.tests import common
import openerp
from openerp.addons.base_report_docx_template.models.parser \
    import ReportDocxReport


class TestParser(common.TransactionCase):
    def setUp(self):
        super(TestParser, self).setUp()

    def test_generate_docx_data(self):
        report = ReportDocxReport(
            'report.report.test', 'report.docx.template'
        )

        attributes = [
            'name', 'users', 'model_access',
            'rule_groups', 'menu_access', 'view_access', 'comment',
            'category_id', 'color', 'full_name', 'share'
        ]

        pool = openerp.registry(self.cr.dbname)
        report.pool = pool
        context = {
            'active_model': 'res.groups'
        }

        data = report.generate_docx_data(self.cr, 1, [1], context)[0]

        res_groups = self.registry('res.groups').browse(self.cr, 1, [1])

        for attribute in attributes:
            self.assertEqual(data[attribute], res_groups[attribute])
