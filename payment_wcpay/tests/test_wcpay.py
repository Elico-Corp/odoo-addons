# -*- coding: utf-8 -*-
from openerp.tests import common
import openerp
import logging
_logger = logging.getLogger(__name__)


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class AcquirerWcpayTestCase(common.TransactionCase):
    def setUp(self):
        super(AcquirerWcpayTestCase, self).setUp()
        self.pay_model = self.env['payment.acquirer']
        self.partner = self.env['res.partner']
        self.country = self.env['res.country']
        self.currency = self.env['res.currency']

    def test_wcpay_form_generate_values(self):
        country = self.country.browse(self.env.cr, self.env.uid, 3)
        state = False
        currency = self.currency.browse(self.env.cr, self.env.uid, 1)
        partner = self.partner.browse(self.env.cr, self.env.uid, 3)

        partner_values = {
            'lang': u'en_US', 'city': u'cc', 'first_name': u'Administrator',
            'last_name': '', 'name': u'Administrator', 'zip': u'cc',
            'country': country, 'country_id': 3, 'phone': u'cc',
            'state': state, 'address': u'cc cc', 'email': u'admin@example.com'
        }
        tx_values = {
            'currency_id': 1, 'currency': currency, 'amount': 1.0,
            'reference': u'SO060', 'partner': partner,
            'return_url': '/shop/payment/validate'
        }
        ids = [15]

        partner_values2, wcpay_tx_values2 = self.pay_model.wcpay_form_generate_values(
            self.env.cr, self.env.uid, ids, partner_values, tx_values)
        pay_link = False
        if wcpay_tx_values2['pay_link']:
            pay_link = True

        self.assertTrue(pay_link)
        self.assertEquals(
            wcpay_tx_values2['notify_url'],
            'http://localhost:6162/payment/weixin/notify')
        self.assertEquals(wcpay_tx_values2['amount'], 1)
        self.assertEquals(wcpay_tx_values2['price'], 1.0)
        self.assertEquals(wcpay_tx_values2['quantity'], 1)

        def test_wcpay_get_form_action_url(self):
            ids = [15]
            url = self.pay_model.wcpay_get_form_action_url(
                self.env.cr, self.env.uid, ids)
            self.assertEquals(
                url, 'https://api.mch.weixin.qq.com/pay/unifiedorder')

        def test_get_providers(self):
            providers = self.pay_model._get_providers(
                self.env.cr, self.env.uid)

            count = providers.count(['wcpay', 'Wechat Pay'])
            self.assertEquals(count, 1)

        def test_connect_wcpay(self):
            currency = self.country.browse(self.env.cr, self.env.uid, 1)
            partner = self.partner.browse(self.env.cr, self.env.uid, 3)

            tx_values = {
                'currency_id': 1, 'currency': currency, 'amount': 1.0,
                'notify_url': u'http://localhost:6162/payment/weixin/notify',
                'reference': u'SO060', 'partner': partner,
                'return_url': '/shop/payment/validate'
            }

            result = self.pay_model._get_providers(
                self.env.cr, self.env.uid, tx_values)

            return_code = result.get('return_code', None)
            self.assertEquals(return_code, 'SUCCESS')
