# -*- coding: utf-8 -*-
# Copyright 2019 Elico Corp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    filter_location_id = fields.Many2one(
        comodel_name='stock.location',
        default=lambda self: self.env.ref('stock.stock_location_stock'))
