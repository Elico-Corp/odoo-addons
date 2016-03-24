# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestAccountInvoice(common.TransactionCase):
    def setUp(self):
        super(TestAccountInvoice, self).setUp()

    def test_is_there_membership_product_is_member(self):
        invoice = self.browse_ref('account.invoice_1')
        invoice.invoice_line[0].product_id = self.browse_ref(
            'membership.membership_2')

        self.assertTrue(invoice._is_there_membership_product())

    def test_is_there_membership_product_not_member(self):
        invoice = self.browse_ref('account.invoice_1')

        self.assertFalse(invoice._is_there_membership_product())
