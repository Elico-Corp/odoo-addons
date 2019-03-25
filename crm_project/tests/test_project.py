# -*- coding: utf-8 -*-
from openerp.tests import common


class TestProject(common.TransactionCase):
    def setUp(self):
        super(TestProject, self).setUp()
        self.project_project = self.env['project.project'].create(
            {'name': 'testing'}
        )

    def test_compute_order_count_is_zero(self):
        """
            Test _compute_order_count for no purchase is found
        """
        self.project_project._compute_order_count()
        self.assertEqual(self.project_project.order_count, 0)

    def test_compute_order_count_with_one_record(self):
        """
            Test _compute_order_count for one purchase is found
        """
        # create a sale order with the project id
        self.sale_order = self.env['sale.order'].create(
            {
                # default value when create a sale order
                'partner_id': 1,
                # set the project id
                'crm_project_id': self.project_project.id
            }
        )
        self.project_project._compute_order_count()
        self.assertEqual(self.project_project.order_count, 1)

    def test_compute_order_count_with_multi_records(self):
        """
            Test _compute_order_count for multi records
        """
        count = 10

        for i in range(0, count):
            # create a sale order with the project id
            self.sale_order = self.env['sale.order'].create(
                {
                    # default value when create a sale order
                    'partner_id': 1,
                    # set the project id
                    'crm_project_id': self.project_project.id
                }
            )

        self.project_project._compute_order_count()
        self.assertEqual(self.project_project.order_count, count)

    def test_action_picking_order_with_empty_domain(self):
        """
            Test action_picking_order with empty domain
        """
        self.env.ref('sale.action_quotations').domain = '[]'
        new_domain = "[('crm_project_id', 'in', %s )]" % str(
            tuple(self.project_project._ids))

        action = self.project_project.action_picking_order()
        self.assertEqual(action['domain'], new_domain)

    def test_action_picking_order_with_domain(self):
        """
            Test action_picking_order with domain
        """
        # create a sale order with the project id
        self.sale_order = self.env['sale.order'].create(
            {
                # default value when create a sale order
                'partner_id': 1,
                # set the project id
                'crm_project_id': self.project_project.id
            }
        )
        self.env.ref('project.open_view_project_all').domain = ['testing']
        old_domain = self.env.ref('sale.action_quotations').domain

        new_domain = "[('crm_project_id', 'in', %s )]" % str(
            tuple(self.project_project._ids))

        action = self.project_project.action_picking_order()

        self.assertNotEqual(action['domain'], old_domain)
        self.assertNotEqual(action['domain'], new_domain)
        self.assertIn(old_domain[1:-1], action['domain'])
        self.assertIn(new_domain[1:-1], action['domain'])

    def test_action_picking_order_with_ctx(self):
        """
            Test action_picking_order with ctx
        """
        self.env.ref('sale.action_quotations').context = "{'1': 'testing'}"
        ctx = self.env.ref('sale.action_quotations').context
        action = self.project_project.action_picking_order()
        self.assertNotEqual(action['context'], ctx)
        self.assertEqual(action['context'], eval(ctx))
