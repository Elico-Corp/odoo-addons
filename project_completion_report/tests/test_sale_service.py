# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.sale.tests.test_sale_common import TestSale


class TestSaleService(TestSale):

    def test_sale_service(self):
        """ Test task creation when confirming a so with the corresponding product """
        project_id = self.env.ref('project.project_project_1')
        # let's log some timesheets
        self.env['account.analytic.line'].create({
            'name': 'Test Line',
            'project_id': project_id.id,
            'unit_amount': 10.5,
        })

        self.issue = self.env['project.issue'].create({
            'name': 'Issue name',
            'project_id': self.project.id,
        })
        analytic_account = self.env['account.analytic.account'].create({
            'name': 'test account',
        })

        self.ProjectObj = self.env['project.project']

        self.AnalyticAccountObject = self.env['account.analytic.account']

        self.AnalyticAccount = self.AnalyticAccountObject.create(
            {'name': 'AnalyticAccount for Test'})

        self.projectA = self.ProjectObj.\
            create({'name': 'Test Project A', 'partner_id': 1,
                    'analytic_account_id': self.AnalyticAccount.id})


        self.ProductObj = self.env['product.product']
        self.productA = self.ProductObj.create(
            {'name': 'Product A', 'uom_id': self.uom_hours.id,
                'uom_po_id': self.uom_hours.id,
                'standard_price': 450})
        self.productB = self.ProductObj.\
            create({'name': 'Product B', 'uom_id': self.uom_hours.id,
                    'uom_po_id': self.uom_hours.id,
                    'standard_price': 550})
        self.productC = self.ProductObj.\
            create({'name': 'Product C', 'uom_id': self.uom_days.id,
                    'uom_po_id': self.uom_days.id,
                    'standard_price': 650})
        self.productD = self.ProductObj.\
            create({'name': 'Product D', 'uom_id': self.uom_kg.id,
                    'uom_po_id': self.uom_kg.id,
                    'standard_price': 750})


        self.task_1 = self.env['project.task'].with_context({
            'mail_create_nolog': True}).create({
            'name': 'Pigs UserTask',
            'project_id': project_id.id
        })

        self.task_2 = self.env['project.task'].with_context({
            'mail_create_nolog': True}).create({
            'name': 'Pigs ManagerTask',
            'user_id': self.user_projectmanager.id,
            'project_id': self.project_pigs.id
        })



        vals = {
            'description': 'test',
            'project_id': self.projectA.id,
            'task_ids': [(0, 0, {'name': 'Test Task'}),
                         (0, 0, {'name': 'Test Task2'})],
        }

        br_obj = self.env['business.requirement']
        br_obj = br_obj.new({'project_id': self.projectA.id})
        br_obj.project_id_change()

        vals.update({'partner_id': br_obj.partner_id.id})

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

        self.env['account.analytic.line'].create({
            'name': 'Test Line',
            'project_id': project_id.id,
            'unit_amount': 39.5,
            'user_id': self.user.id,
        })
        self.assertEqual(so.order_line.qty_delivered, 50, 'Sale Timesheet: timesheet does not increase delivered quantity on so line')
        self.assertEqual(so.invoice_status, 'invoiced', 'Sale Timesheet: "invoice on order" timesheets should not modify the invoice_status of the so')

