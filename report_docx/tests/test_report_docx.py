# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
import openerp
import os
import base64
from openerp.addons.report_docx.report.report_docx \
    import ReportDocx


class TestReportDocx(common.TransactionCase):
    def setUp(self):
        super(TestReportDocx, self).setUp()
        self.pool = openerp.registry(self.cr.dbname)
        self.path = os.path.dirname(__file__)
        file_path = "%s/data/%s" % (self.path, 'testing_template.docx')
        input_stream = open(file_path, 'rb')
        try:
            self.template = base64.b64encode(input_stream.read())
        finally:
            input_stream.close()

        watermark_template_path = "%s/data/%s" % (self.path, 'watermark.pdf')
        input_stream = open(watermark_template_path, 'rb')
        try:
            self.watermark = base64.b64encode(input_stream.read())
        finally:
            input_stream.close()

    def test_generate_docx_data_with_empty(self):
        self.assertEqual([{}], ReportDocx(
            "report.testing.not.data", "testing").generate_docx_data(
            self.cr, 1, [1], {}, {}))

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_create_docx(self):
        context = {
            'name': 'testing report docx',
            'report_name': 'testing report docx',
            'report_type': 'docx',
            'output_type': 'pdf',
            'model': 'res.groups'
        }
        docx_report_id = self.pool.get('ir.actions.report.xml').create(
            self.cr, 1, context)

        docx_report = self.pool.get('ir.actions.report.xml').browse(
            self.cr, 1, docx_report_id)

        report_engine = ReportDocx(
            'report.testing.docx', 'report.docx.template',
        )
        report_engine.pool = openerp.registry(self.cr.dbname)
        report_engine.name = "1234567" + context['report_name']

        with self.assertRaises(Exception):
            report_engine.create(
                self.cr, 1, [report_engine.id], {})

            self.assertEqual(
                self.report_engine.title, docx_report.report_name)

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_create_not_docx(self):
        context = {
            'name': 'testing report not docx',
            'report_name': 'testing report not docx',
            'report_type': 'pdf',
            'model': 'res.groups'
        }

        docx_report_id = self.pool.get('ir.actions.report.xml').create(
            self.cr, 1, context)

        docx_report = self.pool.get('ir.actions.report.xml').browse(
            self.cr, 1, docx_report_id)

        report_engine = ReportDocx(
            'report.testing.not.docx', 'report.docx.template',
        )
        report_engine.pool = openerp.registry(self.cr.dbname)
        report_engine.name = "1234567" + context['report_name']

        self.assertEqual(
            report_engine.create(
                self.cr, 1, [docx_report_id], {}
            ),
            (False, False)
        )
        self.assertEqual(
            report_engine.title, docx_report.report_name)

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_convert_docx_to_pdf_with_watermark_template(self):
        context = {
            'name': 'testing report docx',
            'report_name': 'testing report docx',
            'report_type': 'docx',
            'output_type': 'pdf',
            'model': 'res.groups',
            'watermark_string': 'shadow'
        }
        docx_report_id = self.pool.get('ir.actions.report.xml').create(
            self.cr, 1, context)

        docx_report = self.pool.get('ir.actions.report.xml').browse(
            self.cr, 1, docx_report_id)

        report_engine = ReportDocx(
            'report.testing.convert.pdf.template', 'report.docx.template',
        )
        report_engine.pool = openerp.registry(self.cr.dbname)
        report_engine.name = "1234567" + context['report_name']

        attachment_id = self.pool.get('ir.attachment').create(
            self.cr, 1, {
                'name': 'testing attachment',
                'type': 'binary'
            }
        )

        attachment = self.pool.get('ir.attachment').browse(
            self.cr, 1, attachment_id)
        attachment.db_datas = self.template

        docx_report.template_file = attachment_id

        watermark_id = self.pool.get('ir.attachment').create(
            self.cr, 1, {
                'name': 'watermark',
                'type': 'binary'
            }
        )
        watermark = self.pool.get('ir.attachment').browse(
            self.cr, 1, watermark_id)
        watermark.db_datas = self.watermark

        docx_report.watermark_template = watermark_id

        result = report_engine.create_source_docx(
            self.cr, 1, [1, 2], {'template_id': docx_report_id}, {}
        )

        self.assertEqual(result[1], docx_report.output_type)

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_convert_docx_to_pdf_with_watermark_string(self):
        context = {
            'name': 'testing report docx',
            'report_name': 'testing report docx',
            'report_type': 'docx',
            'output_type': 'pdf',
            'model': 'res.groups',
            'watermark_string': 'shadow'
        }
        docx_report_id = self.pool.get('ir.actions.report.xml').create(
            self.cr, 1, context)

        docx_report = self.pool.get('ir.actions.report.xml').browse(
            self.cr, 1, docx_report_id)

        report_engine = ReportDocx(
            'report.testing.convert.pdf.string', 'report.docx.template',
        )
        report_engine.pool = openerp.registry(self.cr.dbname)
        report_engine.name = "1234567" + context['report_name']

        attachment_id = self.pool.get('ir.attachment').create(
            self.cr, 1, {
                'name': 'testing attachment',
                'type': 'binary'
            }
        )

        attachment = self.pool.get('ir.attachment').browse(
            self.cr, 1, attachment_id)
        attachment.db_datas = self.template

        docx_report.template_file = attachment_id

        result = report_engine.create_source_docx(
            self.cr, 1, [1, 2], {'template_id': docx_report_id}, {}
        )

        self.assertEqual(result[1], docx_report.output_type)

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_convert_docx_to_pdf_without_watermark(self):
        context = {
            'name': 'testing report docx',
            'report_name': 'testing report docx',
            'report_type': 'docx',
            'output_type': 'pdf',
            'model': 'res.groups',
            'watermark_string': False,
            'watermark_template': False
        }
        docx_report_id = self.pool.get('ir.actions.report.xml').create(
            self.cr, 1, context)

        docx_report = self.pool.get('ir.actions.report.xml').browse(
            self.cr, 1, docx_report_id)

        report_engine = ReportDocx(
            'report.testing.convert.pdf.no.watermark', 'report.docx.template',
        )
        report_engine.pool = openerp.registry(self.cr.dbname)
        report_engine.name = "1234567" + context['report_name']

        attachment_id = self.pool.get('ir.attachment').create(
            self.cr, 1, {
                'name': 'testing attachment',
                'type': 'binary'
            }
        )

        attachment = self.pool.get('ir.attachment').browse(
            self.cr, 1, attachment_id)
        attachment.db_datas = self.template

        docx_report.template_file = attachment_id

        result = report_engine.create_source_docx(
            self.cr, 1, [1, 2], {'template_id': docx_report_id}, {}
        )

        self.assertEqual(result[1], docx_report.output_type)

    @openerp.tests.common.at_install(False)
    @openerp.tests.common.post_install(True)
    def test_convert_docx_to_docx(self):
        context = {
            'name': 'testing report docx',
            'report_name': 'testing report docx',
            'report_type': 'docx',
            'output_type': 'docx',
            'model': 'res.groups'
        }
        docx_report_id = self.pool.get('ir.actions.report.xml').create(
            self.cr, 1, context)

        docx_report = self.pool.get('ir.actions.report.xml').browse(
            self.cr, 1, docx_report_id)
        docx_report.watermark_string = 'shadow'

        report_engine = ReportDocx(
            'report.testing.convert.single.docx', 'report.docx.template',
        )
        report_engine.pool = openerp.registry(self.cr.dbname)
        report_engine.name = "1234567" + context['report_name']

        attachment_id = self.pool.get('ir.attachment').create(
            self.cr, 1, {
                'name': 'testing attachment',
                'type': 'binary'
            }
        )

        attachment = self.pool.get('ir.attachment').browse(
            self.cr, 1, attachment_id)
        attachment.db_datas = self.template

        docx_report.template_file = attachment_id

        result = report_engine.create_source_docx(
            self.cr, 1, [1, 2], {'template_id': docx_report_id}, {}
        )

        self.assertEqual(result[1], docx_report.output_type)
