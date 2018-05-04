# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    delivery_detail = fields.Text(string='Delivery Detail')
    refund_detail = fields.Text(string='Refund Detail')
    payment_detail = fields.Text(string='Payment Detail')
    while_stock_last = fields.Text(string='While Stock Last')
    other_detail = fields.Text(string='Others Detail')
    invoice_tc = fields.Text(string='Invoice T&C')
    limit_discount = fields.Float('Limit Discount(%)', help="Discount after \
    which validation of sales is required.")
