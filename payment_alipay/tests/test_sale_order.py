# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestSaleOrder(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        # # create an empty sale order for testing
        self.sale_order = self.env['sale.order'].create(
            {'partner_id': 1}
        )
        # # create an payment acquirer for testing
        self.payment_acquirer = self.env['payment.acquirer'].create(
            {'name': 'alipay', 'provider': 'alipay',
                'website_published': True,
                'alipay_pid': 000000,
                'alipay_seller_email': 'luke.zheng@elico-corp.com',
                'view_template_id': 1,
                'alipay_key': 1,
                'service': 'create_direct_pay_by_user'})

    def test_edi_alipay_url_direct_pay(self):
        """
            Test _edi_alipay_url_direct_pay:
        """
        # search one record
        self.sale_order._edi_alipay_url_direct_pay()
        # state = sent
        self.sale_order.write({'state': 'sent'})
        # service is create_direct_pay_by_user

        self.payment_acquirer.write({
            'service': 'create_direct_pay_by_user'})
        self.sale_order._edi_alipay_url_direct_pay()
        # service is not create_direct_pay_by_user
        self.payment_acquirer.write({
            'service': 'create_partner_trade_by_buyer'})
        self.sale_order._edi_alipay_url_direct_pay()

        # state = cancel
        self.sale_order.write({'state': 'cancel'})
        self.sale_order._edi_alipay_url_direct_pay()

        # create multi payment acquirer for testing
        self.payment_acquirer = self.env['payment.acquirer'].create(
            {'name': 'alipay', 'provider': 'alipay',
                'website_published': True,
                'alipay_pid': 000000,
                'alipay_seller_email': 'luke.zheng@elico-corp.com',
                'view_template_id': 1,
                'alipay_key': 1,
                'service': 'create_direct_pay_by_user'})
        # state = sent
        self.sale_order.write({'state': 'sent'})
        self.sale_order._edi_alipay_url_direct_pay()
        # state = cancel
        self.sale_order.write({'state': 'cancel'})
        self.sale_order._edi_alipay_url_direct_pay()

        # # null payment acquirer for testing
        self.env['payment.acquirer'].unlink()
        self.sale_order._edi_alipay_url_direct_pay()
