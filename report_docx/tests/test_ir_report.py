# -*- coding: utf-8 -*-

from openerp.tests import common
import openerp


class TestIrReport(common.TransactionCase):
    def setUp(self):
        super(TestIrReport, self).setUp()

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_check_selection_field_value_docx(self):
        module = self.registry('ir.actions.report.xml').browse(self.cr, 1, [1])
        self.assertEqual(module._check_selection_field_value(
            'report_type', 'docx'), None)

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_check_selection_field_value_not_docx(self):
        module = self.registry('ir.actions.report.xml').browse(self.cr, 1, [1])

        with self.assertRaises(Exception):
            self.assertEqual(module._check_selection_field_value(
                'report_type', 'None'), None)
