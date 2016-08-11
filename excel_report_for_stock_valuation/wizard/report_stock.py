# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import calendar
import datetime

from openerp import api, fields, models, _


class StockReportQuant(models.TransientModel):
    _name = 'stock.report.quant'

    def _get_first_date(self):
        now = datetime.datetime.now()
        # set the date to the first day of the month
        return datetime.datetime(now.year, now.month, 1)

    def _get_last_date(self):
        now = datetime.datetime.now()
        # return value [first_day, last_day]
        month_range = calendar.monthrange(now.year, now.month)

        # set the date to the end day of the month
        return datetime.datetime(now.year, now.month, month_range[1])

    def _get_default_category(self):
            category_all_id = self.env.ref("product.product_category_all")
            return category_all_id

    def _default_stock_location(self):
        try:
            warehouse = self.env.ref("stock.warehouse0")

            return warehouse.lot_stock_id.id
        except:
            return False

    location_id = fields.Many2one(
        'stock.location', string='Location', required=True,
        default=_default_stock_location)
    start_date = fields.Date(
        'From', required=True, default=_get_first_date)
    end_date = fields.Date(
        'To', required=True, default=_get_last_date)
    category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        required=True,
        default=_get_default_category,
    )

    @api.one
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def print_report(self):
        ctx = {
            'location_id': self.location_id and self.location_id.id or False,
            'location': self.location_id and self.location_id.name or False,
            'category_id': self.category_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        return {
            'name': _('List'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form',
            'res_model': 'report.stock.list',
            'context': ctx,
            'target': 'new',
        }
