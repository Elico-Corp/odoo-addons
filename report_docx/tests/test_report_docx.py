# -*- coding: utf-8 -*-

from openerp.tests import common
from openerp.addons.report_docx.report.report_docx \
    import ReportDocx


class TestReportDocx(common.TransactionCase):
    def setUp(self):
        super(TestReportDocx, self).setUp()

    def test_generate_docx_data_with_empty(self):
        self.assertEqual([{}], ReportDocx(
            "report.testing.not.data", "testing").generate_docx_data(
            self.cr, 1, [1], {}))
