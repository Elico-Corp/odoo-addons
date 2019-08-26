# -*- coding: utf-8 -*-
# © 2019 Elico corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    _sql_constraints = [
        ('credit_debit1', 'CHECK (1=1)', 'Wrong credit or debit value in accounting entry !'),
        ('credit_debit2', 'CHECK (1=1)', 'Wrong credit or debit value in accounting entry !'),
    ]
