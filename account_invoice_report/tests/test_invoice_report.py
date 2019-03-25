# -*- coding: utf-8 -*-
# © 2018 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestInvoiceReport(common.TransactionCase):

    def setUp(self):
        super(TestInvoiceReport, self).setUp()
        self.partner_id = self.env.ref('base.res_partner_1')
        self.account_obj = self.env['account.invoice'].create({
            'partner_id': self.partner_id.id,
            'account_id': 1,
            'invoice_line_ids': [
                (0, 0, {'name': 'test report', 'account_id': 1,
                        'price_unit': 10.00, 'quantity': 1000.00,
                        'discount': 100.00})],
        })

    def test_compute_discount_amount(self):
        self.account_obj._compute_discount_amount()

    def test_compute_original_amount(self):
        self.account_obj._compute_original_amount()
