from openerp.tests import common
import logging
_logger = logging.getLogger(__name__)


class TestPaymentAcquirer(common.TransactionCase):
    def setUp(self):
        super(TestPaymentAcquirer, self).setUp()
        # create an empty sale order for testing
        self.sale_order = self.env['sale.order'].create(
            {'partner_id': 1}
        )
        # create an payment acquirer for testing
        self.payment_acquirer = self.env['payment.acquirer'].create(
            {'name': 'alipay', 'provider': 'alipay',
                'website_published': True,
                'alipay_pid': 000000,
                'alipay_seller_email': 'luke.zheng@elico-corp.com',
                'view_template_id': 1,
                'alipay_key': 1,
                'service': 'create_direct_pay_by_user'})

    def test_get_alipay_urls(self):
        """ Checks if the _get_alipay_urls works properly
        """
        environment = None
        url = self.payment_acquirer._get_alipay_urls(environment)
        alpay_url = {
            'alipay_form_url': 'https://mapi.alipay.com/gateway.do',
        }
        self.assertEqual(url, alpay_url)

    def test_alipay_get_form_action_url(self):
        """
            Alipay URLs
        """
        self.payment_acquirer.alipay_get_form_action_url()

    def test_check_payment_type(self):
        """ Checks if the _check_payment_type works properly
        """
        self.payment_acquirer._check_payment_type()

    def test_get_providers(self):
        """ Checks if the _get_providers works properly
        """
        provider = self.payment_acquirer._get_providers()
        _logger.warning(provider)

    def test_alipay_generate_md5_sign(self):
        """ Checks if the _alipay_generate_md5_sign works properly
        """
        values = {
            'seller_email': u'luke.zheng@elico-corp.com',
            '_input_charset': 'utf-8',
            'notify_url': u'http://192.168.99.100:8070/payment/alipay/notify',
            'partner': False, 'subject': u'SO116',
            'service': u'create_direct_pay_by_user', 'out_trade_no': u'SO116',
            'payment_type': '1', 'total_fee': 0.0, 'sign_type': 'MD5',
            'is_success': 'T',
            'return_url': u'http://192.168.99.100:8070/payment/alipay/return'}
        # inout = 'in'
        inout = 'in'
        acquirer = self.payment_acquirer
        # values has is_success
        md5 = self.payment_acquirer._alipay_generate_md5_sign(
            acquirer, inout, values)
        _logger.warning('md5: ' + md5)
        # values has not is_success
        values.pop('is_success')
        md5 = self.payment_acquirer._alipay_generate_md5_sign(
            acquirer, inout, values)
        _logger.warning('md5: ' + md5)

        # inout = 'out'
        inout = 'out'
        acquirer = self.payment_acquirer
        # service is create_direct_pay_by_user
        md5 = self.payment_acquirer._alipay_generate_md5_sign(
            acquirer, inout, values)
        _logger.warning('md5: ' + md5)
        # service is create_partner_trade_by_buyer
        values.update({'service': 'create_partner_trade_by_buyer'})
        md5 = self.payment_acquirer._alipay_generate_md5_sign(
            acquirer, inout, values)
        _logger.warning('md5: ' + md5)

    def test_alipay_form_generate_values(self):
        """ Checks if the alipay_form_generate_values works properly
        """
        partner_values = {}
        tx_values = {}
        self.payment_acquirer.alipay_form_generate_values(
            partner_values, tx_values)
