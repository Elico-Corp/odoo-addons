# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

import openerp.tests.common as common


class TestMembershipAccountBalanceFuture(common.TransactionCase):
    def setUp(self):
        super(TestMembershipAccountBalanceFuture, self).setUp()
        # partner to be used to test.
        self.partner = self.env['res.partner'].create({
            'name': 'Demo User',
        })
        # accounts to be used: AR/AP/VIP account(with check box checked.)
        account_obj = self.env['account.account']
        user_type_mock = self.ref('account.data_account_type_receivable')
        self.ar_account = account_obj.create({
            'code': 'AR001',
            'name': 'AR account',
            'type': 'receivable',
            'reconcile': True,
            'membership_total': False,
            'user_type': user_type_mock
        })
        self.vip_account = account_obj.create({
            'code': 'VIP001',
            'name': 'VIP account',
            'type': 'other',
            'reconcile': True,
            'membership_total': True,
            'user_type': user_type_mock
        })

        self.vip_journal = self.env['account.journal'].create({
            'name': 'VIP journal',
            'membership': True,
            'code': 'VIP01',
            'default_credit_account_id': self.vip_account.id,
            'default_debit_account_id': self.vip_account.id,
            'company_id': self.ref('base.main_company'),
            'type': 'bank'
        })
        self.bank_statement = self.browse_ref(
            'account.demo_bank_statement_1').copy({
                'journal_id': self.vip_journal.id
            })
        self.pos_order = self.env['pos.order'].create({
            'name': 'fake',
            'pricelist_id': self.ref('product.list0')
        })

        self.period_id = self.ref('account.period_1')
        self.sale_journal_id = self.ref('account.sales_journal')
        self.move = self.env['account.move'].create({
            'name': 'fake',
            'journal_id': self.sale_journal_id
        })
        self.default_account_move_line_val = {
            'name': 'fake',
            'move_id': self.move.id,
            'state': 'valid',
            'period_id': self.period_id,
            'partner_id': self.partner.id,
            'journal_id': self.sale_journal_id,
            'date': date.today()
        }

    def test_00_membership_balance_future(self):
        # first debit and credit and member should all be zero
        partner = self.partner
        self.assertEquals(
            partner.membership_total, 0, 'membership balance should be 0!')
        self.assertEquals(
            partner.membership_total_future, 0,
            'membership balance future should be 0!')

        # create a new bank statement line with the pos_statement
        self.env['account.bank.statement.line'].create({
            'name': 'fake',
            'pos_statement_id': self.pos_order.id,
            'partner_id': self.partner.id,
            'journal_id': self.vip_journal.id,
            'amount': 35,
            'statement_id': self.bank_statement.id
        })
        self.assertEquals(
            partner.membership_total, 0, 'membership balance should be 0!')
        self.assertEquals(
            partner.membership_total_future, -35,
            'membership balance future should be -35!')

    def test_01_proforma_voucher_constraints(self):
        # create a new voucher, over pay, should raise error
        voucher = self.env['account.voucher'].new({
            'amount': 20,
            'partner_id': self.partner.id,
            'journal_id': self.vip_journal.id,
        })
        with self.assertRaises(Exception):
            voucher.button_proforma_voucher()

        # create a new voucher, the invoice type is supplier invoice.
        voucher2 = self.env['account.voucher'].with_context(
            invoice_type='in_invoice').new({
                'amount': 20,
                'partner_id': self.partner.id,
                'journal_id': self.vip_journal.id,
            })
        with self.assertRaises(Exception):
            voucher2.button_proforma_voucher()

        # create a new invoice with membership product in the invoice line.
        invoice = self.browse_ref('account.invoice_1')
        invoice.invoice_line[0].product_id = self.browse_ref(
            'membership.membership_2')
        voucher3 = self.env['account.voucher'].with_context(
            invoice_Id=invoice.id).new({
                'amount': 20,
                'partner_id': self.partner.id,
                'journal_id': self.vip_journal.id,
            })
        with self.assertRaises(Exception):
            voucher3.button_proforma_voucher()

    def test_02_proforma_voucher_pay_with_equals_balance_with_vip_card(self):
        # charge the VIP card for the partner.
        account_move_line_obj = self.env['account.move.line']
        # create a journal entry,
        # the invoice is validated after the member charging
        #   DR: AR
        #   CR: VIP account
        account_move_line_obj.create(dict(
            {'credit': 0, 'debit': 35, 'account_id': self.ar_account.id},
            **self.default_account_move_line_val))
        account_move_line_obj.create(dict({
            'credit': 35,
            'debit': 0,
            'account_id': self.vip_account.id,
        }, **self.default_account_move_line_val))

        # create a new voucher, pay under the VIP card balance.
        voucher = self.env['account.voucher'].new({
            'amount': 35,
            'partner_id': self.partner.id,
            'journal_id': self.vip_journal.id,
        })
        # no raise
        self.assertEquals(voucher.proforma_voucher(), True)

    def test_03_proforma_voucher_pay_with_enough_balance_with_vip_card(self):
        # charge the VIP card for the partner.
        account_move_line_obj = self.env['account.move.line']
        # create a journal entry,
        # the invoice is validated after the member charging
        #   DR: AR
        #   CR: VIP account
        account_move_line_obj.create(dict(
            {'credit': 0, 'debit': 35, 'account_id': self.ar_account.id},
            **self.default_account_move_line_val))
        account_move_line_obj.create(dict({
            'credit': 35,
            'debit': 0,
            'account_id': self.vip_account.id,
        }, **self.default_account_move_line_val))

        # create a new voucher, pay under the VIP card balance.
        voucher = self.env['account.voucher'].new({
            'amount': 20,
            'partner_id': self.partner.id,
            'journal_id': self.vip_journal.id,
        })
        # no raise
        self.assertEquals(voucher.proforma_voucher(), True)

    def test_04_check_enough_membership_balance(self):
        # create a new voucher
        voucher = self.env['account.voucher'].new({
            'amount': 20,
            'partner_id': self.partner.id,
            'journal_id': self.vip_journal.id,
        })
        self.assertEquals(self.partner.membership_total_future, 0)
        self.assertEquals(voucher._check_enough_membership_balance(), False)
        voucher = self.env['account.voucher'].new({
            'amount': 0,
            'partner_id': self.partner.id,
            'journal_id': self.vip_journal.id,
        })
        self.assertEquals(voucher._check_enough_membership_balance(), True)
