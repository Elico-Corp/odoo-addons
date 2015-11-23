# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
