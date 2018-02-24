# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True, ondelete='restrict', index=True)