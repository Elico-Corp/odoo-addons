from openerp.tests import common
import logging
import urllib2
import urllib

_logger = logging.getLogger(__name__)


class TestPaymentAcquirer(common.TransactionCase):
    def setUp(self):
        super(TestPaymentAcquirer, self).setUp()

        # create an empty sale order for testing
        self.sale_order = self.env['sale.order'].create(
            {'partner_id': 1, 'name': u'SO-2015-24059'}
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
            # 'message_follower_ids': [3], 'state_message': False,
            # 'create_date': '2015-09-24 02:54:23',
            'reference': u'SO-2015-24059',
            'write_uid': 1,
            'date_create': '2015-09-24 02:54:23',
            'acquirer_id': self.payment_acquirer.id,
            'fees': 0.0,
            # 'partner_id': (3, u'Administrator'),
            # 'message_ids': [581, 580],
            # 'message_summary': u' ', 'create_uid': (1, u'Administrator'),
            'display_name': u'SO-2015-24059',
            # 'partner_reference': False,
            # 'message_is_follower': True,
            # '__last_update': '2015-09-24 02:55:05',
            # 'partner_name': u'Administrator',
            # 'message_last_post': False,
            'partner_phone': u'1',
            'state': u'draft',
            'alipay_txn_tradeno': False,
            'type': u'form',
            'partner_country_id': 6,
            # 'acquirer_reference': False,
            # 'partner_address': u'q 1',
            # 'partner_email': u'admin@yourcompany.example.com',
            # 'partner_lang': u'en_US',
            'sale_order_id': self.sale_order.id,
            # 'write_date': '2015-09-24 02:55:05',
            # 'partner_zip': u'1',
            'currency_id': 8,
            # 'message_unread': False, 'date_validate': False,
            # 'partner_city': u'1',
            'amount': 0.01, 'website_message_ids': []})
        self.base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')

    # def test_alipay_validate_data(self):
    #     """ Checks if the alipay_validate_data works properly
    #     """

    #     req = urllib2.Request(
    #         self.base_url + '/payment/alipay/notify/')
    #     urllib2.urlopen(req)
        # self.alipay_validate_data(self.return_data)

    def test_alipay_return(self):
        """ Checks if the alipay_return works properly
        """
        url = self.base_url + '/payment/alipay/return/'
        print '------------', url
        post = urllib.urlencode(self.return_data)
        print '1111111111111', post
        req = urllib2.Request(url=url, data=post)
        urllib2.urlopen(req)
