# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Xiaopeng Xie
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
import logging

_logger = logging.getLogger(__name__)


class check_product_qty_wizard(models.TransientModel):
    _name = "check.product.qty.wizard"
    _descript = "Check Product Qty With Mateial"

    product_name = fields.Char(string='产品')
    product_qty = fields.Float(string='数量')
    location_id = fields.Many2one('stock.location', string='库位', default=12)

    @api.one
    def apply(self):
        # if not self.product_name:
        #     return
        product_qty = self.product_qty
        product_qty = product_qty if product_qty > 1 else 1

        domain = [
            '|',
            ('name_template', 'like', self.product_name),
            ('default_code', 'like', self.product_name)
        ]
        products = self.env['product.product'].search(domain)
        bom_map = self.calculate_product_bom_weight(products, product_qty)

        line_obj = self.env['check.product.qty.report']
        lines = line_obj.search([])
        lines.unlink()
        self.praepare_report(bom_map)

        action = self.go_to_tree_view()
        return action

    @api.multi
    def go_to_tree_view(self):
        mod_obj = self.env['ir.model.data']
        action_id = mod_obj.get_object_reference(
            'check_product_qty_with_material',
            'action_check_product_qty_report_tree')
        action_id = action_id and action_id[1]

        final_url = "/web#page=0&limit=&view_type=list&model=check.product.qty.report&" + \
            "action=" + str(action_id)

        return {
            'type': 'ir.actions.act_url',
            'url': final_url,
            'target': 'self'
        }

    def calculate_product_bom_weight(self, products, product_qty):
        bom_map = []
        for product in products:
            bom = self.env['mrp.bom'].search(
                [('product_id', '=', product.id)], limit=1)
            if bom:
                bom_lines = self.get_final_components(
                    bom.bom_line_ids, 0, product_qty)
                bom_map2 = {
                    'product_id': bom.product_id.id,
                    'product_qty': 1 * product_qty,
                    'childs': bom_lines,
                    'level': 0,
                }
                bom_map2 = self.analyze_bom_map([bom_map2], [[bom_map2]])
                bom_map.append(bom_map2[0])
        return bom_map

    def praepare_report(self, bom_map):
        product_obj = self.env['product.product']
        line_obj = self.env['check.product.qty.report']

        for bom in bom_map:
            product_id = bom.get('product_id', None)
            product = product_obj.browse(product_id)
            name = "[" + product.default_code + "]" + product.name
            product_qty = bom.get('product_qty', 0)
            can_product_qty = bom.get('can_product_qty', 0)
            diff_qty = product_qty - can_product_qty if product_qty - can_product_qty >0 else 0

            vals = {
                'product_name': bom.get('level', 1) * "------" + name,
                'product_qty': product_qty,
                'stock_qty': bom.get('stock_qty', 0),
                'can_product_qty': bom.get('can_product_qty', 0),
                'diff_qty': diff_qty,
            }
            line_obj.create(vals)

            child_bom = bom.get('childs', None)
            if child_bom:
                self.praepare_report(child_bom)

    @api.multi
    def analyze_bom_map(self, bom_map, bom_list):
        product_obj = self.pool.get('product.product')
        for bom in bom_map:
            child_bom = bom.get('childs', False)
            if child_bom:
                bom_list.append(child_bom)
                self.analyze_bom_map(child_bom, bom_list)
            else:
                need_qty = bom.get('product_qty', 0)
                product_id = bom.get('product_id', None)
                if product_id:
                    context = self.env.context
                    if self.location_id.id:
                        context = {'location': self.location_id.id}
                    product = product_obj.browse(
                        self.env.cr, self.env.uid, product_id, context)
                    # get stock qty
                    stock_qty = product.qty_available
                    can_product_qty = int(stock_qty / need_qty)
                    vals = {
                        'stock_qty': stock_qty,
                        'can_product_qty': can_product_qty,
                    }
                    bom.update(vals)

        self.analyze_bom_map2(bom_list)
        return bom_map

    @api.multi
    def analyze_bom_map2(self, bom_list):
        bom_list = sorted(
            bom_list, key=lambda bom: bom[0].get('level', 0), reverse=True)

        for bom in bom_list:
            can_product_qty = 0
            can_product_qty = min([x.get('can_product_qty', 0) + (x.get('stock_qty', 0) if x.get('childs', False) else 0) for x in bom])
            for bom2 in bom_list:
                for line in bom2:
                    if line.get('childs', False) == bom:
                        line['can_product_qty'] = can_product_qty

    @api.multi
    def get_final_components(self, bom_line_ids, level, product_qty):
        bom_lines = []
        for line in bom_line_ids:
            if not line.child_line_ids:
                val = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty * product_qty,
                    'level': level + 1,
                }
                bom_lines.append(val)
            else:
                val = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty * product_qty,
                    'childs': self.get_final_components(
                        line.child_line_ids, level + 1, product_qty),
                    'level': level + 1,
                }
                bom_lines.append(val)
        return bom_lines
