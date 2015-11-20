# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Siyuan Gu
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
from openerp import models, fields, api, _
import calendar
import datetime


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

    @api.one
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def print_report(self):
        ctx = {
            'location_id': self.location_id and self.location_id.id or False,
            'location': self.location_id and self.location_id.name or False,
            'start_date': self.start_date,
            'end_date': self.end_date
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
