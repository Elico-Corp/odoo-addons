# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


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

    def create_action(self, cr, uid, ids, context=None):
        """ Create a contextual action for each of the report."""
        for ir_actions_report_xml in self.browse(
                cr, uid, ids, context=context):
            ir_values_id = self.pool['ir.values'].create(cr, SUPERUSER_ID, {
                'name': ir_actions_report_xml.name,
                'model': ir_actions_report_xml.model,
                'key2': 'client_print_multi',
                'value': "ir.actions.report.xml,%s" %
                         ir_actions_report_xml.id,
            }, context)
            ir_actions_report_xml.write({
                'ir_values_id': ir_values_id,
            })
        return True

    def unlink_action(self, cr, uid, ids, context=None):
        """ Remove the contextual actions created for the reports."""
        self.check_access_rights(cr, uid, 'write', raise_exception=True)
        for ir_actions_report_xml in self.browse(
                cr, uid, ids, context=context):
            if ir_actions_report_xml.ir_values_id:
                try:
                    self.pool['ir.values'].unlink(
                        cr, SUPERUSER_ID,
                        ir_actions_report_xml.ir_values_id.id, context
                    )
                except Exception:
                    # raise UserError(
                    #     _('Deletion of the action record failed.')
                    # )
                    raise Exception(
                        _('Deletion of the action record failed.')
                    )
        return True
