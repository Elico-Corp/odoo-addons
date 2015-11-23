# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright Liping Wang
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


class accountInvoice(models.Model):
    _inherit = 'account.invoice'

    discount_amount = fields.Float(
        string='Discount Amount', compute='_discount_amount')
    original_amount = fields.Float(
        string='Original Amount', compute='_original_amount')

    @api.one
    @api.depends('invoice_line')
    def _discount_amount(self):
        discount_amount = 0.0
        for line in self.invoice_line:
            discount_amount += line.price_unit * line.discount / 100 \
                * line.quantity
        self.discount_amount = discount_amount

    @api.one
    @api.depends('invoice_line')
    def _original_amount(self):
        original_amount = 0.0
        for line in self.invoice_line:
            original_amount += line.price_unit * line.quantity
        self.original_amount = original_amount
