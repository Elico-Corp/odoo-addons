# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#    Eric Caudal <eric.caudal@elico-corp.com>
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
import unittest2
from datetime import datetime, timedelta
import openerp
import openerp.tests.common as common
from openerp.osv import osv

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_sale(object):

    def configure(self):
        # get super user
        self.m = self.registry('ir.model.data')
        # get companies
        self.company_origin = self.m.get_object(
            self.cr, self.uid, 'base_intercompany', 'company_origin')

        self.company_destination = self.m.get_object(
            self.cr, self.uid, 'base_intercompany', 'company_destination')

        self.user_origin = self.m.get_object(
            self.cr, self.uid, 'base_intercompany', 'user_origin')

        self.user_destination = self.m.get_object(
            self.cr, self.uid, 'base_intercompany', 'user_destination')

        self.shop_origin = self.m.get_object(
            self.cr, self.uid, 'base_intercompany_sale', 'shop_origin')

        self.backend_origin = self.m.get_object(
            self.cr, self.uid, 'base_intercompany', 'backend_origin')

        self.backend_destination = self.m.get_object(
            self.cr, self.uid, 'base_intercompany', 'backend_destination')

    def set_backend(self, on_create=True, on_write=True,
                    on_unlink=True, on_confirm=True, on_cancel=True):
        assert hasattr(self, 'concept')
        backend_pool = self.registry('icops.backend')
        backend_pool.write(self.cr, ADMIN_USER_ID, self.backend_origin.id, {
            'icops_ids': [(5, 0), (0, 0, {
                'backend_id': self.backend_origin.id,
                'backend_to': self.backend_destination.id,
                'concept': self.concept,
                'on_create': on_create,
                'on_write': on_write,
                'on_unlink': on_unlink,
                'on_confirm': on_confirm,
                'on_cancel': on_cancel
            })]
        })

    def create_object(self):
        pool_origin = self.registry(self.model_origin)
        uid = self.user_origin.id
        obj_id = pool_origin.create(
            self.cr, self.user_origin.id, self.data_obj)
        obj = pool_origin.browse(self.cr, uid, obj_id)
        bind_ids = obj.icops_bind_ids
        self.assertEqual(len(bind_ids), 1)
        bind_id = bind_ids[0]
        icops_ids = bind_id.icops_ids
        self.assertEqual(len(icops_ids), 1)
        icops = icops_ids[0]
        ic_uid = icops.backend_id.icops_uid
        self.assertEqual(icops.model, self.model_destination)
        pool_destination = self.registry(icops.model)
        obj_dest = pool_destination.browse(
            self.cr, ic_uid, icops.record_id)
        self.assertIsNotNone(obj_dest)
        return obj, obj_dest

    def write_object(self, obj, obj_dest):
        pool_origin = self.registry(self.model_origin)
        uid = self.user_origin.id
        self.assertEqual(len(obj.order_line), 0)
        self.assertEqual(len(obj_dest.order_line), 0)
        pool_origin.write(self.cr, uid, obj.id, {
            'order_line': [(5, 0), (0, 0, self.data_line)]
        })
        self.assertEqual(len(obj.order_line), 2)
        self.assertEqual(len(obj_dest.order_line), 2)


    def test_01_creation(self):
        self.set_backend()
        self.create_object()

    def test_02_creation_raise_exception(self):
        self.set_backend(on_create=False)
        self.assertRaises(
            osv.except_osv, self.create_object)

    def test_03_creation_without_write_permission(self):
        self.set_backend(on_write=False)
        self.create_object()

    # def test_04_write(self):
    #     self.set_backend()
    #     pool_origin = self.registry(self.model_origin)
    #     obj, obj_dest = self.create_object()
    #     self.write_object(obj, obj_dest)


class test_sale_so2po(common.TransactionCase, test_sale):

    def setUp(self):
        super(test_sale_so2po, self).setUp()
        self.configure()
        self.concept = 'so2po'
        self.model_origin = 'sale.order'
        self.model_destination = 'purchase.order'
        self.data_obj = {
            'partner_id': self.company_destination.partner_id.id,
            'partner_invoice_id': self.company_destination.partner_id.id,
            'partner_shipping_id': self.company_destination.partner_id.id,
            'shop_id': self.shop_origin.id,
            'date_order': datetime.now().strftime('%Y-%m-%d'),
            'pricelist_id': self.user_origin.property_product_pricelist.id}

        self.data_line = {
            'name': 'Test product',
            'product_uom': 1,
            'product_uom_qty': 1,
            'price_unit': 100
        }


class test_sale_so2so(common.TransactionCase, test_sale):

    def setUp(self):
        super(test_sale_so2so, self).setUp()
        self.configure()
        self.concept = 'so2so'
        self.model_origin = 'sale.order'
        self.model_destination = 'sale.order'
        self.data_obj = {
            'partner_id': self.company_destination.partner_id.id,
            'partner_invoice_id': self.company_destination.partner_id.id,
            'partner_shipping_id': self.company_destination.partner_id.id,
            'shop_id': self.shop_origin.id,
            'date_order': datetime.now().strftime('%Y-%m-%d'),
            'pricelist_id': self.user_origin.property_product_pricelist.id}

        self.data_line = {
            'name': 'Test product',
            'product_uom': 1,
            'product_uom_qty': 1,
            'price_unit': 100
        }
# class test_sale_po2so(common.TransactionCase, test_sale):

#     def setUp(self):
#         super(test_sale_po2so, self).setUp()
#         self.configure()
#         self.model_origin = 'purchase.order'
#         self.model_destination = 'sale.order'
