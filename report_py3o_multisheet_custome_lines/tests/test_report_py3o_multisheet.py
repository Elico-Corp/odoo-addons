# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
import os


class TestReportPy3oMultisheet(common.TransactionCase):

    def setUp(self):
        super(TestReportPy3oMultisheet, self).setUp()
        self.report_py3o_multisheet_model = self.env['report.py3o.multisheet']

    def test_create_new_template(self):
        Test_sheet_lines_data = {
            'Sheet1': {
                'name': 'Sheet1',
                'lines': 16,
                'duplicate': True,
                'head_end_line': 20,
                'sequence': 1
            },
            'Sheet2': {
                'name': 'Sheet2',
                'lines': 16,
                'duplicate': True,
                'head_end_line': 20,
                'sequence': 2
            },
            'Sheet3': {
                'name': 'Sheet3',
                'lines': 4,
                'duplicate': True,
                'head_end_line': 20,
                'sequence': 3
            }
        }
        attribute_num_per_line = 9
        attribute_per_line = [
            '${data.line%d.index}',
            '${data.line%d.hs_code.hs_code}',
            '${data.line%d.hs_code.name}',
            '${data.line%d.qty}',
            '${data.ship_to}',
            '${data.ship_from}',
            '${data.line%d.unit_price}',
            '${data.line%d.total}',
            '${data.line%d.pricelist}',
            '${data.line%d.hs_code.cn_name}',
            '${data.line%d.hs_code.uom_id.name}', ]
        new_path = "/tests/customs_declaration_report_template_new.ods"
        base_path = "/tests/customs_declaration_report_template.ods"
        template_new_path =\
            os.path.dirname(os.path.dirname(__file__)) + '/' + new_path
        template_base_path =\
            os.path.dirname(os.path.dirname(__file__)) + '/' + base_path
        doc = self.report_py3o_multisheet_model.open_base_template(
            template_base_path)
        sheets = doc.sheets
        self.report_py3o_multisheet_model.multi_sheet_per_template(
            sheets, Test_sheet_lines_data)
        self.report_py3o_multisheet_model.multi_lines_per_sheet(
            sheets, Test_sheet_lines_data)
        self.report_py3o_multisheet_model.multi_attribute_per_line(
            sheets,
            Test_sheet_lines_data,
            attribute_per_line,
            attribute_num_per_line)
        self.report_py3o_multisheet_model.save_new_template(
            template_new_path,
            doc
        )
