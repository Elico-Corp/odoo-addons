# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
import mock


class TestReportPy3oMultisheet(common.TransactionCase):

    def setUp(self):
        super(TestReportPy3oMultisheet, self).setUp()
        self.report_xml_id = self.env.ref('report_py3o_convert_xlsx.'
                                          'res_users_report_py3o_xlsx')
        self.users_list = self.env['res.users'].search([])

    def test_report_generate_xlsx(self):
        with mock.patch('requests.post') as patched_post:
            magick_response = mock.MagicMock()
            magick_response.status_code = 200
            patched_post.return_value = magick_response
            magick_response.iter_content.return_value = "test result"
            self.report_xml_id.render_report(
                self.env.user.ids, self.report_xml_id.report_name, {})
