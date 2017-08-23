# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
import os


class TestReportPy3oMultisheet(common.TransactionCase):

    def setUp(self):
        super(TestReportPy3oMultisheet, self).setUp()
        self.report_py3o_multisheet_model = self.env['report.py3o.multisheet']
        self.report_py3o_model = self.env['py3o.report']

    def test_create_new_template(self):
        Test_sheet_lines_data = {
            'Sheet1': {
                'name': 'Sheet1',
                'lines': 16,
                'duplicate': True,
                'head_end_line': 14,
                'sequence': 1,
                'lines_number': 2
            },
            'Sheet2': {
                'name': 'Sheet2',
                'lines': 16,
                'duplicate': True,
                'head_end_line': 14,
                'sequence': 2,
                'lines_number': 4
            },
            'Sheet3': {
                'name': 'Sheet3',
                'lines': 4,
                'duplicate': True,
                'head_end_line': 14,
                'sequence': 3,
                'lines_number': 8
            }
        }
        attribute_num_per_line = 9
        attribute_per_line = [
            '${data.line%d.index}',
            '${data.line%d.hs_code.hs_code}',
            '${data.line%d.hs_code.name}',
            '${data.line%d.qty}',
            '${objects.ship_info_id%d.ship_to.country_id.name}',
            '${objects.ship_info_id%d.ship_from.country_id.name}',
            '${data.line%d.unit_price}',
            '${data.line%d.total}',
            '${data.line%d.pricelist}',
            '${data.line%d.hs_code.cn_name}',
            '${data.line%d.hs_code.uom_id.name}', ]
        new_path = "tests/customs_declaration_report_template_new.ods"
        base_path = "tests/customs_declaration_report_template.ods"
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

    def test_render_report_with_data(self):
        template_new = "tests/delivery_sheet_per_pallet_template_new.ods"
        template_base = "tests/delivery_sheet_per_pallet_template.ods"
        template_new_path = \
            os.path.dirname(
                os.path.dirname(__file__)) + '/' + template_new
        template_base_path = \
            os.path.dirname(os.path.dirname(__file__)) + '/' + template_base
        head_end_line = 9
        attribute_per_line = [
            '${line%d.client_order_ref}',
            '${line%d.product_id.customer_product_code}',
            '${line%d.product_id.name}',
            '${line%d.product_uom}',
            '${line%d.product_uom_qty}',
            '${line%d.qty_delivery}',
            '${line%d.carton_qty}',
        ]
        summary_line = [
            '${%s.sum_qty}',
            '${%s.sum_qty_delivery}',
            '${%s.pallet_sum}'
        ]
        lines_per_sheet = [
            {
                'name': '28ctns',
                'lines_number': 6,
                'list': [
                    'package1',
                    'package2',
                    'package3'
                ]
            },
            {
                'name': '29ctns',
                'lines_number': 4,
                'list': [
                    'package3',
                    'package4'
                ]
            }
        ]
        self.report_py3o_multisheet_model\
            .template_sheet_with_custom_line(
                head_end_line,
                lines_per_sheet,
                attribute_per_line,
                summary_line,
                template_new_path,
                template_base_path)

    def test_create_new_tmp_folder(self):
        tmp_folder_name = \
            self.report_py3o_multisheet_model._get_tmp_folder()
        self.report_py3o_multisheet_model._create_tmp_folder(tmp_folder_name)
        os.system('touch ' + tmp_folder_name + '/report/res_user.odt')
        demo_report_action = self.env.ref('report_py3o.res_users_report_py3o')
        demo_report_action.write(
            {
                'py3o_template_fallback': 'report/res_user.odt',
                'py3o_template_fallback_base': 'report/res_user.odt',
            }
        )
        demo_report_py3o = self.report_py3o_model.create(
            {'ir_actions_report_xml_id': demo_report_action.id}
        )
        template_new = demo_report_action.py3o_template_fallback
        demo_report_py3o._get_template_from_path(
            tmp_folder_name + template_new)
