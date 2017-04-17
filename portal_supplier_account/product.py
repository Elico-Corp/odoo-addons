# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Qing Wang <qing.wang@elico-corp.com>
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
from openerp import models, api, fields

NUMBER_OF_PROCUREMENT_ROUTES_TO_CHECK = 3


class product_product(models.Model):
    _inherit = 'product.product'

    supplier_stock_count = fields.Integer('Stock Count')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Groups',
        compute='_product_user_id',
        store=True
    )

    @api.one
    @api.depends('seller_ids')
    def _product_user_id(self):
        partner_ids = []
        for seller in self.seller_ids:
            partner_ids.append(seller.name.id)
        self.supplier_ids = [(6, 0, partner_ids)]

    def _check_user_is_supplier(self, cr, uid, context=None):
        """
            Check if current user in Portal Supplier Account Group
        """
        group_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid,
            'portal_supplier_account',
            'res_portal_supplier_account')[1]

        user = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        res_group = self.pool.get(
            'res.groups').browse(cr, uid, group_id, context=context)
        return bool(user) if user in res_group.users else False

    def _add_supplier_info(self, cr, uid, product_id, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        supplier_info = {
            'return_instructions': False,
            'name': user.partner_id.id,
            'sequence': 1,
            'company_id': 1,
            'delay': 1,
            'warranty_return_other_address_id': False,
            'warranty_duration': 0,
            'pricelist_ids': [],
            'warranty_return_partner': 'company',
            'min_qty': 0,
            'product_code': False,
            'product_name': False,
            'active_supplier': False,
            'direct_delivery_flag': True,
            'product_tmpl_id': product_id,
        }

        self.pool.get(
            'product.supplierinfo').create(
            cr, uid, supplier_info, context=context)

    def create(self, cr, uid, vals, context=None):
        product_id = super(
            ProductTemplate, self).create(cr, uid, vals, context=context)
        check_result = self._check_user_is_supplier(
            cr, uid, context=context)
        if check_result and not self.browse(cr, uid, product_id).seller_ids:
            self._add_supplier_info(cr, uid, product_id, context=context)
        return product_id

    @api.multi
    def write(self, vals):
        product_id = super(ProductTemplate, self).write(vals)
        check_result = self._check_user_is_supplier()
        if check_result and not self.browse(self.id).seller_ids:
            self._add_supplier_info(self.id)
        return product_id


class sale_order(models.Model):
    _inherit = 'sale.order'

    supplier_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Groups',
        compute='_order_user_id',
        store=True
    )

    @api.one
    @api.depends('order_line')
    def _order_user_id(self):
        partner_ids = []
        for line in self.order_line:
            product = line.product_id
            if len(product.route_ids) == NUMBER_OF_PROCUREMENT_ROUTES_TO_CHECK:
                partner_ids.append(product.supplier_ids.id)
        self.supplier_ids = [(6, 0, partner_ids)]


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    supplier_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Groups',
        compute='_stock_user_id',
        store=True
    )

    # dropshipping
    group_user_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Group user',
        compute='_group_user_id',
        store=True
    )

    @api.one
    @api.depends('sale_id')
    def _stock_user_id(self):
        partner_ids = []
        if self.sale_id:
            for supplier in self.sale_id.supplier_ids:
                partner_ids.append(supplier.id)
        self.supplier_ids = [(6, 0, partner_ids)]

    @api.one
    @api.depends('group_id')
    def _group_user_id(self):
        partner_ids = []
        if self.group_id:
            sale_orders = self.env['sale.order'].search(
                [('procurement_group_id.id', '=', self.group_id.id)])
            for sale_order in sale_orders:
                for supplier in sale_order.supplier_ids:
                    partner_ids.append(supplier.id)
        self.group_user_ids = [(6, 0, partner_ids)]
