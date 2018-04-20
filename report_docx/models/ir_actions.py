# -*- coding: utf-8 -*-
# © 2018 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    ir_values_id = fields.Many2one(
        comodel_name='ir.values',
        string='More Menu entry',
        readonly=True,
        help='More menu entry.',
        copy=False
    )

    report_type = fields.Selection(
        selection_add=[(('docx', 'Docx'))]
    )

    template_file = fields.Many2one(
        comodel_name='ir.attachment',
        string='Template File'
    )

    watermark_string = fields.Char(
        string='Wartermark String'
    )

    watermark_template = fields.Many2one(
        comodel_name='ir.attachment',
        string='Watermark Template'
    )

    output_type = fields.Selection(
        [
            ('pdf', 'PDF'),
            ('docx', 'Docx'),
        ],
        'Output Type',
        required=True,
        default='pdf'
    )

    @api.multi
    def create_action(self):
        """ Create a contextual action for each of the report."""

        for ir_actions_report_xml in self:
            ir_values_id = self.env['ir.values'].sudo().create( {
                'name': ir_actions_report_xml.name,
                'model': ir_actions_report_xml.model,
                'key2': 'client_print_multi',
                'value': "ir.actions.report.xml,%s" %
                         ir_actions_report_xml.id,
            })
            ir_actions_report_xml.write({
                'ir_values_id': ir_values_id.id,
            })
        return True

    @api.multi
    def unlink_action(self):
        """ Remove the contextual actions created for the reports."""
        self.check_access_rights('write', raise_exception=True)
        for ir_actions_report_xml in self:
            if ir_actions_report_xml.ir_values_id.id:
                try:
                    self.env['ir.values'].sudo().browse(
                        ir_actions_report_xml.ir_values_id.id).unlink()
                except Exception:
                    raise Exception(
                        _('Deletion of the action record failed.')
                    )
        return True
