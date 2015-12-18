# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import tempfile

import xlrd
from openerp import api, fields, models, _
from openerp.osv import osv


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
