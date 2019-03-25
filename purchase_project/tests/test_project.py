# -*- coding: utf-8 -*-
from openerp.tests import common


class TestProject(common.TransactionCase):
    def setUp(self):
        super(TestProject, self).setUp()
        self.project_project = self.env['project.project'].create(
            {'name': 'testing'}
        )

    def test_compute_purchase_count_is_zero(self):
        """
            Test _compute_purchase_count for no purchase is found
        """
        self.project_project._compute_purchase_count()
        self.assertEqual(self.project_project.purchase_count, 0)

    def test_compute_purchase_count_with_one_record(self):
        """
            Test _compute_purchase_count for one purchase is found
        """
        # create a purchase order with the project id
        self.purchase_order = self.env['purchase.order'].create(
            {
                # default value when create a purchase order
                'partner_id': 1,
                'location_id': 1,
                'pricelist_id': 1,
                # set the project id
                'project_id': self.project_project.id
            }
        )
        self.project_project._compute_purchase_count()
        self.assertEqual(self.project_project.purchase_count, 1)

    def test_compute_purchase_count_with_multi_records(self):
        """
            Test _compute_purchase_count for multi purchase
        """
        count = 10
        for i in range(0, count):
            # create a purchase order with the project id
            self.purchase_order = self.env['purchase.order'].create(
                {
                    # default value when create a purchase order
                    'partner_id': 1,
                    'location_id': 1,
                    'pricelist_id': 1,
                    # set the project id
                    'project_id': self.project_project.id
                }
            )
        self.project_project._compute_purchase_count()
        self.assertEqual(self.project_project.purchase_count, count)

    def test_action_picking_purchase_with_empty_domain(self):
        """
            Test action_picking_purchase with empty domain
        """
        self.env.ref('purchase.purchase_rfq').domain = '[]'
        new_domain = "[('project_id', 'in', %s )]" % str(
            tuple(self.project_project._ids))

        action = self.project_project.action_picking_purchase()
        self.assertEqual(action['domain'], new_domain)

    def test_action_picking_purchase_with_domain(self):
        """
            Test action_picking_purchase with domain
        """
        self.env.ref('purchase.purchase_rfq').domain = ['testing']
        old_domain = self.env.ref('purchase.purchase_rfq').domain

        new_domain = "[('project_id', 'in', %s )]" % str(
            tuple(self.project_project._ids))

        action = self.project_project.action_picking_purchase()

        self.assertNotEqual(action['domain'], old_domain)
        self.assertNotEqual(action['domain'], new_domain)
        self.assertIn(old_domain[1:-1], action['domain'])
        self.assertIn(new_domain[1:-1], action['domain'])

    def test_action_picking_purchase_with_ctx(self):
        """
            Test action_picking_purchase with ctx
        """
        self.env.ref('purchase.purchase_rfq').context = \
            "{'1': 'testing'}"
        ctx = self.env.ref('purchase.purchase_rfq').context
        action = self.project_project.action_picking_purchase()

        self.assertNotEqual(action['context'], ctx)
        self.assertEqual(action['context'], eval(ctx))
