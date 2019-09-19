# -*- coding: utf-8 -*-
# Copyright 2019 Elico Corp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def name_get(self):
        """
        Return the qty can be used if context get `show_qty`.
        """
        filter_location_id = self._context.get('filter_location_id', False)
        res = []
        if self._context.get('show_qty') and filter_location_id:
            Quant = self.env['stock.quant']
            for lot in self:
                quant_ids = Quant.search([
                    ('lot_id', '=', lot.id), ('location_id', 'child_of', filter_location_id)])
                qty = sum(quant_ids.mapped('qty'))
                res.append((lot.id, '{} ({})'.format(lot.name, qty)))
            return res
        return super(StockProductionLot, self).name_get()
