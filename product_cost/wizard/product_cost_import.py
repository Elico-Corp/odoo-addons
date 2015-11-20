# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia<liu.lixia@elico-corp.com>
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
from openerp.osv import osv
import xlrd
import tempfile


class ProductCostImport(models.TransientModel):

    _name = 'product.cost.import'
    _description = 'Generate product cost for all selected manufacture order'

    product_file = fields.Binary(string="File", filters='*.xlsx')

    @api.multi
    def import_sheet(self):
        if not self.product_file and not self.env.context.get('active_id'):
            raise osv.except_osv(
                _("Warning!"),
                _("You must select xlsx file to import product cost(s)."))
        batch_id = self.env.context.get('active_id')
        file_path = tempfile.gettempdir() + '/file.xlsx'
        f = open(file_path, 'wb')
        f.write(self.product_file.decode('base64'))
        f.close()
        product_cost_batch = self.env['product.cost.batch'].browse(batch_id)
        product_cost = self.env['product.cost']
        mrp_production = self.env['mrp.production']
        product_cost_batch.cost_ids.unlink()
        wb = xlrd.open_workbook(file_path)
        table = wb.sheet_by_index(0)
        nrows = table.nrows
        for num in range(2, nrows):
            mrp = mrp_production.search(
                [('name', '=', table.row_values(num)[0])])
            customer_id = False
            if mrp:
                if mrp.sale_name:
                    sale_obj = self.env['sale.order'].search(
                        [('name', '=', mrp.sale_name)])
                    customer_id = sale_obj.partner_id.id
                res = {
                    'cost_batch_id': batch_id,
                    'mo_id': mrp.id,
                    'customer_id': customer_id,
                    'product_name': mrp.product_id.id,
                    'finished_product_number': table.row_values(num)[5],
                    'sale_income': table.row_values(num)[6],
                    'material_cost': table.row_values(num)[7],
                    'resource_cost': table.row_values(num)[8],
                    'manufacture_cost': table.row_values(num)[9],
                    'total': table.row_values(num)[10],
                    'sale_profit': table.row_values(num)[11],
                    'sale_profit_percent': table.row_values(num)[12],
                    'unit_material_cost': table.row_values(num)[13],
                    'unit_resource_cost': table.row_values(num)[14],
                    'unit_manufacture_cost': table.row_values(num)[15],
                    'unit_cost': table.row_values(num)[16],
                }
                product_cost.create(res)
        return {'type': 'ir.actions.act_window_close'}
