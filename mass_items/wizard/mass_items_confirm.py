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

from openerp import models, api, fields, _
from openerp.exceptions import Warning


class MassItemsConfirm(models.TransientModel):
    _name = 'mass.items.confirm'
    _description = 'Confirm mass items'

    message = fields.Text('Message')

    # return the product list ids from the lines
    def _get_product_ids_in_order_lines(self):
        parent_model = self._context['parent_model']
        parent_id = self._context['parent_id']
        model_pool = self.env[parent_model].browse(parent_id)

        product_lines = []
        if parent_model in ("sale.order", "purchase.order"):
            product_lines = model_pool.order_line
        elif parent_model in ("stock.picking",):
            product_lines = model_pool.move_lines
        elif parent_model in ("stock.inventory",):
            product_lines = model_pool.line_ids
        else:
            raise Warning(
                _(
                    """The model:%s
                    is not supported for massing adding lines!"""
                    % (parent_model)
                )
            )

        return [line.product_id for line in product_lines]

    # return the mass product ids list from the wizard
    def _get_product_ids_in_mass_product_items(self):
        mass_items = self.env['mass.items.quantities'].browse(
            self._context.get('active_id'))

        return [
            (line.product, line.quantity) for line in mass_items.item_lines
        ]

    # add the products into the lines
    def _add_product_items(self, product_and_quantity):
        # generate the product lines base on the product ids
        lines = []
        parent_model = self._context['parent_model']
        parent_id = self._context['parent_id']
        model_record = self.env[parent_model].browse(parent_id)

        for product, quantity in product_and_quantity:
            if "sale.order" == parent_model:
                lines.append({
                    "product_id": product.id,
                    "product_uom_qty": quantity,
                })
            elif "purchase.order" == parent_model:
                lines.append({
                    "product_id": product.id,
                    "product_qty": quantity,
                    "price_unit": 0,
                    "name": product.name,
                    "date_planned": fields.datetime.now()
                })
            elif "stock.picking" == parent_model:
                picking = model_record.picking_type_id
                lines.append({
                    "product_id": product.id,
                    "product_uom": product.uom_id.id,
                    "product_uom_qty": quantity,
                    "location_id": picking.default_location_src_id,
                    "location_dest_id": picking.default_location_dest_id,
                    "name": product.name,
                })
            elif "stock.inventory" == parent_model:
                lines.append({
                    "product_id": product.id,
                    "product_uom_id": product.uom_id.id,
                    "product_qty": quantity,
                    "location_id": model_record.location_id
                })
            else:
                raise Warning(
                    _(
                        """The model:%s
                        is not supported for massing adding lines!"""
                        % (parent_model)
                    )
                )

        if parent_model in ("sale.order", "purchase.order"):
            # write the products into the order lines
            model_record.order_line = lines
        elif parent_model in ("stock.picking"):
            # write the products into the order lines
            model_record.move_lines = lines
        elif parent_model in ("stock.inventory"):
            model_record.line_ids = lines

    # do not add the duplicated product into the line
    @api.one
    def add_products_without_duplicate(self):
        # get product list ids from the lines
        orderlines = self._get_product_ids_in_order_lines()
        # get the mass product ids list from the wizard
        mass_items = self._get_product_ids_in_mass_product_items()

        # remove the duplicate ids in the mass product ids
        product_and_quantity = [
            (product, quantity) for [product, quantity] in mass_items
            if product not in orderlines
        ]

        # add prodcuts into lines
        self._add_product_items(product_and_quantity)

        return {'type': 'ir.actions.act_window_close'}

    # add all the products from the mass items wizard into the lines
    @api.one
    def add_products(self):
        # get the mass product ids list from the wizard
        product_and_quantity = self._get_product_ids_in_mass_product_items()

        # add prodcuts into lines
        self._add_product_items(product_and_quantity)

        return {'type': 'ir.actions.act_window_close'}
