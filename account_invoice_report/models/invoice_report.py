# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    discount_amount = fields.Float(
        string='Discount Amount', compute='_compute_discount_amount')
    original_amount = fields.Float(
        string='Original Amount', compute='_compute_original_amount')

    @api.one
    @api.depends('invoice_line')
    def _compute_discount_amount(self):
        discount_amount = 0.0
        for line in self.invoice_line:
            discount_amount += line.price_unit * line.discount / 100 \
                * line.quantity
        self.discount_amount = discount_amount

    @api.one
    @api.depends('invoice_line')
    def _compute_original_amount(self):
        original_amount = 0.0
        for line in self.invoice_line:
            original_amount += line.price_unit * line.quantity
        self.original_amount = original_amount
