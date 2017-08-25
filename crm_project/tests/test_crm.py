# -*- coding: utf-8 -*-
from openerp.tests import common


class TestProject(common.TransactionCase):
    def setUp(self):
        super(TestProject, self).setUp()
        self.crm_lead = self.env['crm.lead'].create(
            {'name': 'testing'}
        )

    def test_compute_project_count_is_zero(self):
        """
            Test _compute_project_count for no purchase is found
        """
        self.crm_lead._compute_project_count()
        self.assertEqual(self.crm_lead.project_count, 0)

    def test_compute_project_count_with_one_record(self):
        """
            Test _compute_project_count for one purchase is found
        """
        # create a project with the crm id
        self.project_project = self.env['project.project'].create(
            {
                'name': 'testing',
                'opportunity_id': self.crm_lead.id
            }
        )
        self.crm_lead._compute_project_count()
        self.assertEqual(self.crm_lead.project_count, 1)

    def test_compute_project_count_with_multi_records(self):
        """
            Test _compute_project_count for multi records
        """
        count = 10

        for i in range(0, count):
            # create a project with the crm id
            self.project_project = self.env['project.project'].create(
                {
                    'name': 'testing',
                    'opportunity_id': self.crm_lead.id
                }
            )
        self.crm_lead._compute_project_count()
        self.assertEqual(self.crm_lead.project_count, count)

    def test_action_picking_with_empty_domain(self):
        """
            Test action_picking with empty domain
        """
        self.env.ref('project.open_view_project_all').domain = '[]'
        new_domain = "[('opportunity_id', 'in', %s )]" % str(
            tuple(self.crm_lead._ids))

        action = self.crm_lead.action_picking()
        self.assertEqual(action['domain'], new_domain)

    def test_action_picking_with_domain(self):
        """
            Test aciont_picking with domain
        """
        # create a project with the crm id
        self.project_project = self.env['project.project'].create(
            {
                'name': 'testing',
                'opportunity_id': self.crm_lead.id
            }
        )
        self.env.ref('project.open_view_project_all').domain = ['testing']
        old_domain = self.env.ref('project.open_view_project_all').domain

        new_domain = "[('opportunity_id', 'in', %s )]" % str(
            tuple(self.crm_lead._ids))

        action = self.crm_lead.action_picking()

        self.assertNotEqual(action['domain'], old_domain)
        self.assertNotEqual(action['domain'], new_domain)
        self.assertIn(old_domain[1:-1], action['domain'])
        self.assertIn(new_domain[1:-1], action['domain'])

    def test_action_picking_order_with_ctx(self):
        """
            Test action_picking with ctx
        """
        self.env.ref('project.open_view_project_all').context = \
            "{'1': 'testing'}"
        ctx = self.env.ref('project.open_view_project_all').context
        action = self.crm_lead.action_picking()
        self.assertNotEqual(action['context'], ctx)
        self.assertEqual(action['context'], eval(ctx))
