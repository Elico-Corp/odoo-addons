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
from openerp import models, fields, api


class ReportStockList(models.TransientModel):
    _name = 'report.stock.list'

    def _get_location(self):
        location = self.env['stock.location'].search(
            [('id', '=', self._context.get('location_id', False))]
        )

        return location

    def _get_sale_name_from_source(self, origin_and_sales_name, source):
        return origin_and_sales_name.get(source) or ""

    def _get_product_inventory(self, stock_historys, origin_and_sales_name):
        products = {}
        for stock_history in stock_historys:
            sale_name = self._get_sale_name_from_source(
                origin_and_sales_name, stock_history.source)

            key = str(stock_history.product_id.id) + ":" + sale_name

            quantity = stock_history.quantity
            value = stock_history.inventory_value

            if key in products.keys():
                products[key] = {
                    "quantity": products[key]["quantity"] + quantity,
                    "inventory_value":
                        products[key]["inventory_value"] + value,
                    "product": stock_history.product_id
                }
            else:
                products[key] = {
                    "quantity": quantity,
                    "inventory_value": value,
                    "product": stock_history.product_id
                }

        return products

    def _get_product_inventory_before_start_date(self, origin_and_sales_name):
        start_date = self._context['start_date']
        location_id = self._context['location_id']

        stock_historys = self.env['stock.history'].search([
            ('date', '<', start_date),
            ('location_id', '=', location_id),
            ('quantity', '!=', 0)
        ])

        return self._get_product_inventory(
            stock_historys, origin_and_sales_name)

    def _get_product_inventory_at_end_date(self, origin_and_sales_name):
        end_date = self._context['end_date']
        location_id = self._context['location_id']

        stock_historys = self.env['stock.history'].search([
            ('date', '<=', end_date),
            ('location_id', '=', location_id),
            ('quantity', '!=', 0)
        ])

        return self._get_product_inventory(
            stock_historys, origin_and_sales_name)

    def _get_product_inventory_between_date(self, origin_and_sales_name):
        start_date = self._context['start_date']
        end_date = self._context['end_date']
        location_id = self._context['location_id']

        stock_historys = self.env['stock.history'].search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('location_id', '=', location_id),
            ('quantity', '!=', 0)
        ])

        products = {}

        for stock_history in stock_historys:
            sale_name = self._get_sale_name_from_source(
                origin_and_sales_name, stock_history.source)

            key = str(stock_history.product_id.id) + ":" + sale_name

            quantity = stock_history.quantity
            value = stock_history.inventory_value

            if key in products.keys():
                if quantity > 0:
                    products[key]["in_quantity"] = products[key]["in_quantity"] + quantity
                    products[key]["in_inventory_value"] = products[key]["in_inventory_value"] + value
                else:
                    products[key]["out_quantity"] = products[key]["out_quantity"] + quantity
                    products[key]["out_inventory_value"] = products[key]["out_inventory_value"] + value

            else:
                products[key] = {
                    "in_quantity": 0,
                    "in_inventory_value": 0,
                    "out_quantity": 0,
                    "out_inventory_value": 0,
                    "product": stock_history.product_id
                }

                if quantity > 0:
                    products[key]["in_quantity"] = quantity
                    products[key]["in_inventory_value"] = value
                else:
                    products[key]["out_quantity"] = quantity
                    products[key]["out_inventory_value"] = value

        return products

    # This function join the below tabels:
    #   sale_order
    #   mrp_production
    #   purchase_order
    #   stock_move
    #   res_users
    # It returns the possible sales order name for the specific
    # purchase order, sales order, or manufacturing order.
    #
    # Notice:
    #   Normall the format of the origin in purchase order or manufacturing
    #   order is <SO:PO> or <SO:MO>
    #
    #   To avoid the duplicated SO name like SO001 and SO0010
    #   ":" is added after <SO> from sale order.
    #
    # Example:
    # origin  | name
    # ---------+-------
    #         |
    # PO00008 | SO008
    # SO005   | SO005
    # MO00003 | SO008
    # MO00005 | SO008
    # PO00009 |
    # PO00006 |
    # MO00002 |
    # MO00006 | SO009
    # MO00001 |
    # MO00004 | SO009
    # SO009   | SO009
    # SO008   | SO008
    # PO00002 |

    def _get_source_from_sql(self):
        user_id = self._context['uid']

        self._cr.execute("""
            select t.origin, s.name
            FROM
            (
                select move.origin, sale_order.name
                FROM stock_move as move
                LEFT JOIN
                    mrp_production ON mrp_production.name = move.origin
                LEFT JOIN
                    purchase_order ON purchase_order.name = move.origin
                LEFT JOIN
                    sale_order ON position(
                        sale_order.name || ':' in mrp_production.origin) > 0 or
                    position(
                        sale_order.name || ':' in purchase_order.origin) > 0
                GROUP BY
                    move.origin,sale_order.name
            ) as t
            LEFT JOIN
                sale_order as s
            ON
                t.name = s.name or t.origin = s.name
            JOIN res_users u
                on u.id = %s
            GROUP BY
                t.origin, s.name;
        """ % user_id)

        return {rec[0]: rec[1] for rec in self._cr.fetchall()}

    def _load_lines(self):
        origin_and_sales_name = self._get_source_from_sql()
        res = []

        lines_before = self._get_product_inventory_before_start_date(
            origin_and_sales_name)
        lines_end = self._get_product_inventory_at_end_date(
            origin_and_sales_name)
        lines = self._get_product_inventory_between_date(origin_and_sales_name)

        for key, product in lines_before.items():
            if key not in lines.keys() and product["quantity"] != 0:
                product_id = product['product']

                val = {
                    "source": key.split(':')[1],
                    "product_id": product_id.name,
                    "default_code": product_id.default_code or "",
                    "cate": product_id.categ_id.name,
                    "month_inventory": product["quantity"],
                    "month_inventory_value": product["inventory_value"],
                    "stock_in": 0,
                    "stock_in_real_cost": 0,
                    "stock_in_inventory_value": 0,
                    "stock_out": 0,
                    "stock_out_real_cost": 0,
                    "stock_out_inventory_value": 0,
                    "stock": product["quantity"],
                    "stock_inventory_value":
                        product["inventory_value"]
                }

                if 0 == product["quantity"]:
                    val['month_real_cost'] = 0
                else:
                    val['month_real_cost'] = abs(
                        product["inventory_value"] /
                        product["quantity"]
                    )
                val['stock_real_cost'] = val['month_real_cost']

                res.append(val)

        for key, product in lines.items():

            product_id = product['product']

            val = {
                "source": key.split(':')[1],
                "product_id": product_id.name,
                "default_code": product_id.default_code or "",
                "cate": product_id.categ_id.name,
                "stock":
                    lines_end[key]["quantity"],
                "stock_inventory_value":
                    lines_end[key]["inventory_value"]
            }

            val["stock_in"] = product["in_quantity"]
            val["stock_in_inventory_value"] = product["in_inventory_value"]
            if 0 == val["stock_in"]:
                val["stock_in_real_cost"] = 0
            else:
                val["stock_in_real_cost"] = val["stock_in_inventory_value"] / val["stock_in"]

            val["stock_out"] = -product["out_quantity"]
            val["stock_out_inventory_value"] = -product["out_inventory_value"]
            if 0 == val["stock_out"]:
                val["stock_out_real_cost"] = 0
            else:
                val["stock_out_real_cost"] = val["stock_out_inventory_value"] / val["stock_out"]

            if key in lines_before.keys():
                val['month_inventory'] = lines_before[key]["quantity"]
                val['month_inventory_value'] = lines_before[key]["inventory_value"]

                if 0 == lines_before[key]["quantity"]:
                    val['month_real_cost'] = 0
                else:
                    val['month_real_cost'] = abs(
                        lines_before[key]["inventory_value"] /
                        lines_before[key]["quantity"]
                    )
            else:
                val['month_inventory'] = 0
                val['month_real_cost'] = 0
                val['month_inventory_value'] = 0

            if 0 == lines_end[key]["quantity"]:
                val['stock_real_cost'] = 0
            else:
                val['stock_real_cost'] = abs(
                    lines_end[key]["inventory_value"] /
                    lines_end[key]["quantity"]
                )

            res.append(val)

        return sorted(res, key=lambda rec: (rec['product_id'], rec['source']))

    def _get_table_titile(self):
        # save the format in col:title
        title = {
            0: "Product",
            1: "Source",
            2: "Default Code",
            3: "Cate",
            4: "Month Inventory",
            5: "Month Inventory",
            6: "Month Inventory value",
            7: "Stock in",
            8: "Stock in real cost",
            9: "Stock in inventory value",
            10: "Stock out",
            11: "Stock out real cost",
            12: "Stock out inventory value",
            13: "Stock",
            14: "Stock real cost",
            15: "Stock inventory value",
        }

        return title

    def _get_company_name(self):
        uid = self._context['uid']

        user = self.env['res.users'].search(
            [('id', '=', uid)]
        )

        return user and user.company_id and user.company_id.name or ""

    lines = fields.One2many(
        'stock.quant.line', 'list_id',
        readonly=True, default=_load_lines
    )

    location_id = fields.Many2one(
        'stock.location', string='Location', readonly=True,
        required=True, default=_get_location)

    @api.one
    def export(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def xls_export(self):
        datas = {
            'model': 'report.stock.list',
            'title': self._get_table_titile(),
            'start_date': self._context['start_date'] or "",
            'end_date': self._context['end_date'] or "",
            'location': self._context['location'] or "",
            'company': self._get_company_name()
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.valuation.report.xls',
            'datas': datas
        }


class StockQuantLine(models.TransientModel):
    _name = 'stock.quant.line'

    list_id = fields.Many2one(
        'report.stock.list', ondelete='cascade', index=True)
    product_id = fields.Char(readonly=True, default="")
    source = fields.Char(readonly=True, default="")
    default_code = fields.Char(readonly=True, default="")
    cate = fields.Char(readonly=True, default="")
    month_inventory = fields.Float(readonly=True, default=0)
    month_real_cost = fields.Float(readonly=True, default=0)
    month_inventory_value = fields.Float(readonly=True, default=0)
    stock_in = fields.Float(readonly=True, default=0)
    stock_in_real_cost = fields.Float(readonly=True, default=0)
    stock_in_inventory_value = fields.Float(readonly=True, default=0)
    stock_out = fields.Float(readonly=True, default=0)
    stock_out_real_cost = fields.Float(readonly=True, default=0)
    stock_out_inventory_value = fields.Float(readonly=True, default=0)
    stock = fields.Float(readonly=True, default=0)
    stock_real_cost = fields.Float(readonly=True, default=0)
    stock_inventory_value = fields.Float(readonly=True, default=0)
