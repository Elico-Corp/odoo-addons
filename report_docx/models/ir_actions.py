# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[(('docx', 'Docx'))])

    template_file = fields.Many2one(
        comodel_name='ir.attachment', string='Template File')

    watermark_string = fields.Char(string='Wartermark String')

    watermark_template = fields.Many2one(
        comodel_name='ir.attachment', string='Watermark Template')

    output_type = fields.Selection(
        [
            ('pdf', 'PDF'),
            ('docx', 'Docx'),
        ],
        'Output Type', required=True, default='pdf'
    )
