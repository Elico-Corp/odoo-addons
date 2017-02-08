# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests.common as common
from datetime import date


class TestPartnerDebitCreditMembershipBalance(common.TransactionCase):

    ''' this class is mainly test the debit & credit
    & membership balance'''

    def setUp(self):
        super(TestPartnerDebitCreditMembershipBalance, self).setUp()
        # partner to be used to test.
        self.partner = self.env['res.partner'].create({
            'name': 'Alex Duan',
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
        self.ap_account = account_obj.create({
            'code': 'AP001',
            'name': 'AP account',
            'type': 'payable',
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
        self.bank_account = account_obj.create({
            'code': 'BANK001',
            'name': 'Bank account',
            'type': 'liquidity',
            'reconcile': False,
            'membership_total': False,
            'user_type': user_type_mock
        })
        self.sale_income_account = account_obj.create({
            'code': 'SI001',
            'name': 'Sales Income account',
            'type': 'other',
            'reconcile': False,
            'membership_total': False,
            'user_type': user_type_mock
        })

        # default period id & sale journal id
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

    def test_00_debit_credit_membership_balance(self):
        ''' test an AR/AP/Membership account '''
        # first debit and credit and member should all be zero
        partner = self.partner
        self.assertEquals(partner.debit, 0, 'Partner debit should be 0!')
        self.assertEquals(partner.credit, 0, 'Partner credit should be 0!')
        self.assertEquals(
            partner.membership_total, 0, 'membership balance should be 0!')

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

        # check the debit/credit/membership balance.
        self.assertEquals(partner.debit, 0, "partner debit should be 0!")
        self.assertEquals(partner.credit, 35, 'Partner credit should be 35!')
        self.assertEquals(
            partner.membership_total, 35, 'membership balance should be 35!')

        # create a new journal entry, membership pays for the invoice.
        #   DR: Bank
        #   CR: AR
        account_move_line_obj.create(dict({
            'credit': 0,
            'debit': 35,
            'account_id': self.bank_account.id,
        }, **self.default_account_move_line_val))
        account_move_line_obj.create(dict({
            'credit': 35,
            'debit': 0,
            'account_id': self.ar_account.id,
        }, **self.default_account_move_line_val))

        # check the debit/credit/membership balance.
        self.assertEquals(partner.debit, 0, "partner debit should be 0!")
        self.assertEquals(partner.credit, 0, 'Partner credit should be 0!')
        self.assertEquals(
            partner.membership_total, 35, 'membership balance should be 35!')

        # create a new journal entry,
        # membership buys the products, invoice validated.
        #   CR: Sale Income
        #   DR: AR
        account_move_line_obj.create(dict({
            'credit': 0,
            'debit': 20,
            'account_id': self.ar_account.id,
        }, **self.default_account_move_line_val))
        account_move_line_obj.create(dict({
            'credit': 20,
            'debit': 0,
            'account_id': self.sale_income_account.id,
        }, **self.default_account_move_line_val))
        # check the debit/credit/membership balance.
        self.assertEquals(partner.debit, 0, "partner debit should be 0!")
        self.assertEquals(partner.credit, 20, 'Partner credit should be 20!')
        self.assertEquals(
            partner.membership_total, 35, 'membership balance should be 35!')

        # create a new journal entry,
        # membership pays for the invoice by using VIP card.
        #   CR: AR
        #   DR: VIP account
        account_move_line_obj.create(dict({
            'credit': 0,
            'debit': 20,
            'account_id': self.vip_account.id,
        }, **self.default_account_move_line_val))
        account_move_line_obj.create(dict({
            'credit': 20,
            'debit': 0,
            'account_id': self.ar_account.id,
        }, **self.default_account_move_line_val))
        # check the debit/credit/membership balance.
        self.assertEquals(partner.debit, 0, "partner debit should be 0!")
        self.assertEquals(partner.credit, 0, 'Partner credit should be 0!')
        self.assertEquals(
            partner.membership_total, 15, 'membership balance should be 15!')
