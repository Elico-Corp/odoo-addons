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
import openerp.tests.common as common


class TestBackend(common.TransactionCase):
    """
    test generic Backend
    """

    def setUp(self):
        super(TestBackend, self).setUp()

    def tearDown(self):
        super(TestBackend, self).tearDown()

    def test_product_cost(self):
        mrp = self.env.ref('mrp.mrp_production_1')
        product_cost_batch = self.env['product.cost.batch'].create(
            {'name': 'test'})
        res = {'cost_batch_id': product_cost_batch.id,
               'mo_id': mrp.id,
               'customer_id': False,
               'product_name': mrp.product_id.id,
               'finished_product_number': 1,
               'sale_income': 500,
               'material_cost': 50,
               'resource_cost': 100,
               'manufacture_cost': 100
               }
        product_cost = self.env['product.cost'].create(res)
        assert product_cost.total == (product_cost.material_cost +
                                      product_cost.resource_cost +
                                      product_cost.manufacture_cost)
        assert product_cost.sale_profit == (product_cost.sale_income -
                                            product_cost.total)
