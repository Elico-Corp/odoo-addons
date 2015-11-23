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
from openerp import models, fields


class company(models.Model):
    _inherit = 'res.company'

    delivery_detail = fields.Text(string='Delivery Detail')
    refund_detail = fields.Text(string='Refund Detail')
    payment_detail = fields.Text(string='Payment Detail')
    while_stock_last = fields.Text(string='While Stock Last')
    other_detail = fields.Text(string='Others Detail')
    invoice_tc = fields.Text(string='Invoice T&C')
    limit_discount = fields.Float('Limit Discount(%)',
            help="Discount after which validation of sales is required.")
