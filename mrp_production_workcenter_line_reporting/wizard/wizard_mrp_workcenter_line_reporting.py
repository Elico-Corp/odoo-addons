# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class WizardMrpWorkcenterLineReporting(models.TransientModel):
    _name = 'wizard.mrp.workcenter.line.reporting'

    def _get_date(self):
        return fields.Date.context_today(self)

    date = fields.Date(
        'Date', required=True, default=_get_date)
    finished_qty = fields.Float(
        required=True, string="Finished Quantity",
    )
    scraped_qty = fields.Float(
        string="Scraped Quantity",
    )
    scraped_reason_id = fields.Many2one(
        'mrp.workcenter.line.scraped.reason',
        string='Scraped Reason')

    def _write_record(self):
        active_id = self._context['active_id']
        obj = self.env['mrp.workcenter.line.reporting']

        val = {
            'workcenter_line_id': active_id,
            'date': self.date,
            'finished_qty': self.finished_qty,
            'scraped_qty': self.scraped_qty,
            'scraped_reason_id':
            self.scraped_reason_id and self.scraped_reason_id.id or False
        }

        obj.create(val)

    @api.one
    def save(self):
        self._write_record()

        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class MrpWorkcenterLineReporting(models.Model):
    _name = 'mrp.workcenter.line.reporting'
    _order = 'date'

    workcenter_line_id = fields.Integer()
    date = fields.Date('Date')
    finished_qty = fields.Float()
    scraped_qty = fields.Float()
    scraped_reason_id = fields.Many2one(
        'mrp.workcenter.line.scraped.reason',
        string='Scraped Reason')


class MrpWorkcenterLineReason(models.Model):
    _name = 'mrp.workcenter.line.scraped.reason'
    _rec_name = 'reason'

    reason = fields.Char(string="Reason")
