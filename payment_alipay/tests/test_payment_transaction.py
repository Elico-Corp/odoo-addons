# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
import logging
_logger = logging.getLogger(__name__)


class TestPaymentTransaction(common.TransactionCase):
    def setUp(self):
        super(TestPaymentTransaction, self).setUp()

        # create an payment acquirer for testing
        self.payment_acquirer = self.env['payment.acquirer'].create(
            {'name': 'alipay', 'provider': 'alipay',
                'website_published': True,
                'alipay_pid': 000000,
                'alipay_seller_email': 'luke.zheng@elico-corp.com',
                'view_template_id': 1,
                'alipay_key': 1,
                'service': 'create_direct_pay_by_user'})
        self.sale_order = self.env['sale.order'].create(
            {'partner_id': 1,
                'name': 'SO-2015-18-0050'}
        )
        # create an transaction
        self.payment_transaction = self.env['payment.transaction'].create(
            {'reference': 'SO-2015-18-0050',
                'acquirer_id': self.payment_acquirer.id,
                'sale_order_id': self.sale_order.id,
                'amount': 0,
                'currency_id': 1,
                'partner_country_id': 1})
        self.return_data = {
            'seller_email': u'sales@elico-corp.com',
            'trade_no': u'2015092421001004960098491428',
            'seller_id': u'2088701568026380',
            'buyer_email': u'cialuo@126.com',
            'subject': u'SO-2015-24059',
            'sign': u'31ec60b33f2dd89fff2557bfd06cad6f',
            'exterface': u'create_direct_pay_by_user',
            'out_trade_no': u'SO-2015-24059',
            'payment_type': u'1', 'total_fee': u'0.01',
            'sign_type': u'MD5',
            'notify_time': u'2015-09-24 10:55:01',
            'trade_status': u'TRADE_SUCCESS',
            'notify_id': u'RqPnCoPT3K9%2Fvwbh3InVbTzrlGy8Nc02ac3vWSajRn%2BhdZXlGj0vsq%2FpszXQ5%2B7FyuNo',
            'notify_type': u'trade_status_sync',
            'is_success': u'T', 'buyer_id': u'2088002451351968'}
        self.payment_transaction = self.env['payment.transaction'].create({
            'message_follower_ids': [3], 'state_message': False,
            'create_date': '2015-09-24 02:54:23',
            'reference': u'SO-2015-24059', 'write_uid': (1, u'Administrator'),
            'date_create': '2015-09-24 02:54:23',
            'acquirer_id': (4, u'Alipay'),
            'fees': 0.0, 'partner_id': (3, u'Administrator'),
            'message_ids': [581, 580],
            'message_summary': u' ', 'create_uid': (1, u'Administrator'),
            'display_name': u'SO-2015-24059', 'partner_reference': False,
            'message_is_follower': True,
            '__last_update': '2015-09-24 02:55:05',
            'partner_name': u'Administrator', 'message_last_post': False,
            'partner_phone': u'1', 'id': 3, 'state': u'draft',
            'alipay_txn_tradeno': False,
            'type': u'form', 'partner_country_id': (6, u'Albania'),
            'acquirer_reference': False,
            'partner_address': u'q 1',
            'partner_email': u'admin@yourcompany.example.com',
            'partner_lang': u'en_US', 'sale_order_id': (12, u'SO-2015-24059'),
            'write_date': '2015-09-24 02:55:05',
            'partner_zip': u'1', 'currency_id': (8, u'CNY'),
            'message_unread': False, 'date_validate': False,
            'partner_city': u'1', 'amount': 0.01, 'website_message_ids': []})

    def test_alipay_form_get_tx_from_data(self):
        """ Checks if the _alipay_form_get_tx_from_data works properly
        """

        # can find the reference
        # sign is right
        self.payment_transaction._alipay_form_get_tx_from_data(
            self.return_data)
        # sign is not right
        self.return_data.update({'sign': 'SO-2015-18-0050'})
        with self.assertRaises(Exception):
            self.payment_transaction._alipay_form_get_tx_from_data(
                self.return_data)
        # can not find the reference
        self.return_data.update({'out_trade_no': 'SO-2015-18-0050'})
        with self.assertRaises(Exception):
            self.payment_transaction._alipay_form_get_tx_from_data(
                self.return_data)

        # does not have out_trade_no
        self.return_data.pop('out_trade_no')
        with self.assertRaises(Exception):
            self.payment_transaction._alipay_form_get_tx_from_data(
                self.return_data)

    def test_alipay_form_get_invalid_parameters(self):
        """ Checks if the _alipay_form_get_invalid_parameters works properly
        """
        self.payment_transaction._alipay_form_get_invalid_parameters(
            self.payment_transaction, self.return_data)

    def test_alipay_form_validate(self):
        """ Checks if the _alipay_form_validate works properly
        """
        self.payment_transaction._alipay_form_validate(
            self.payment_transaction, self.return_data)
