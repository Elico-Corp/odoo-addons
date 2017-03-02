# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'
    session_id = fields.Many2one(
        'pos.session', 'POS Session')


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.one
    @api.depends('statement_ids')
    def _get_line_ids(self):
        line_ids = []
        for bankstate in self.statement_ids:
            line_ids.extend(bankstate.line_ids)
        self.statement_line_ids = [l.id for l in line_ids]

    statement_line_ids = fields.One2many(
        'account.bank.statement.line',
        'session_id',
        string="Payment Lines",
        compute='_get_line_ids',
        readonly=True,
        copy=False)
