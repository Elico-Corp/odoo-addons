# -*- coding: utf-8 -*-
# © 2016 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestSaleService(common.TransactionCase):
    def setUp(self):
        super(TestSaleService, self).setUp()

    def test_report(self):
        project_id = self.env.ref('project.project_project_1')
        self.ProjectObj = self.env['project.project']

        self.AnalyticAccountObject = self.env['account.analytic.account']
        self.AnalyticLinAccountObject = self.env['account.analytic.line']
        self.AnalyticAccount = self.AnalyticAccountObject.create(
            {'name': 'AnalyticAccount for Test'})

        # Configure unit of measure.
        self.categ_wtime = self.ref('product.uom_categ_wtime')
        self.categ_kgm = self.ref('product.product_uom_categ_kgm')

        self.projectA = self.ProjectObj.\
            create({'name': 'Test Project A', 'partner_id': 1,
                    'analytic_account_id': self.AnalyticAccount.id})
        self.projectB = self.ProjectObj.\
            create({'name': 'Test Project B', 'partner_id': 1,
                    'analytic_account_id': self.AnalyticAccount.id})
        self.UomObj = self.env['product.uom']
        self.uom_hours = self.UomObj.create({
            'name': 'Test-Hours',
            'category_id': self.categ_wtime,
            'factor': 8,
            'uom_type': 'smaller'})
        self.uom_days = self.UomObj.create({
            'name': 'Test-Days',
            'category_id': self.categ_wtime,
            'factor': 1})
        self.uom_kg = self.UomObj.create({
            'name': 'Test-KG',
            'category_id': self.categ_kgm,
            'factor_inv': 1,
            'factor': 1,
            'uom_type': 'reference',
            'rounding': 0.000001})

        self.ProductObj = self.env['product.product']
        self.productA = self.ProductObj.create({
            'name': 'Product A', 'uom_id': self.uom_hours.id,
            'uom_po_id': self.uom_hours.id,
            'standard_price': 450
        })
        self.productB = self.ProductObj.create({
            'name': 'Product B', 'uom_id': self.uom_hours.id,
            'uom_po_id': self.uom_hours.id,
            'standard_price': 550
        })
        self.productC = self.ProductObj.create({
            'name': 'Product C',
            'uom_id': self.uom_days.id,
            'uom_po_id': self.uom_days.id,
            'standard_price': 650
        })
        self.productD = self.ProductObj.create({
            'name': 'Product D', 'uom_id': self.uom_kg.id,
            'uom_po_id': self.uom_kg.id,
            'standard_price': 750
        })

        vals = {
            'description': 'test',
            'project_id': project_id.id,
            'task_ids': [
                (0, 0, {
                    'name': 'Test Line',
                    'project_id': project_id.id,
                    'planned_hours': 10,
                }),
                (0, 0, {
                    'name': 'Test Line',
                    'project_id': project_id.id,
                    'planned_hours': 30,
                })]
        }
        ts1 = self.AnalyticLinAccountObject.create({
            'name': 'Test Line',
            'project_id': project_id.id,
            'unit_amount': 30,
        })

        ts2 = self.AnalyticLinAccountObject.create({
            'name': 'Test Line',
            'project_id': project_id.id,
            'unit_amount': 40,
        })

        ts3 = self.AnalyticLinAccountObject.create({
            'name': 'Test Line',
            'project_id': project_id.id,
            'unit_amount': 25,
        })

        self.brA = self.env['business.requirement'].create(vals)
        self.brA.write({
            'deliverable_lines': [
                (0, 0, {'name': 'deliverable line1', 'qty': 1.0,
                        'unit_price': 900, 'uom_id': 1,
                        'business_requirement_id': self.brA.id,
                        'resource_ids': [
                            (0, 0, {
                                'name': 'Resource Line1',
                                'product_id': self.productA.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'resource_type': 'task',
                                'business_requirement_id': self.brA.id
                            }),
                            (0, 0, {
                                'name': 'Resource Line1',
                                'product_id': self.productB.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'resource_type': 'task',
                                'business_requirement_id': self.brA.id
                            })]}),
                (0, 0, {'name': 'deliverable line2', 'qty': 1.0,
                        'business_requirement_id': self.brA.id,
                        'unit_price': 1100, 'uom_id': 1}),
                (0, 0, {'name': 'deliverable line3', 'qty': 1.0,
                        'business_requirement_id': self.brA.id,
                        'unit_price': 1300, 'uom_id': 1}),
                (0, 0, {'name': 'deliverable line4', 'qty': 1.0,
                        'business_requirement_id': self.brA.id,
                        'unit_price': 1500, 'uom_id': 1,
                        })
            ]})
        planned_hours = 0
        remaining_hours = 0
        for hours in self.brA.task_ids:
            planned_hours += hours.planned_hours
        remaining_hours += ts1.unit_amount + ts2.unit_amount + ts3.unit_amount
        rl_hours = 0
        for rl in self.brA.deliverable_lines:
            for hours in rl.resource_ids:
                rl_hours += hours.qty
        extra_hours = rl_hours - remaining_hours
        self.assertEqual(extra_hours, 105.0)
        self.assertEqual(planned_hours, 40.0)
