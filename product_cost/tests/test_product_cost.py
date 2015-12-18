# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
