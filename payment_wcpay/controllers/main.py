# -*- coding: utf-8 -*-
import logging
import pprint
import urlparse
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.web.http import route
from openerp.addons.report.controllers.main import ReportController
from openerp.addons.payment_wcpay.models.weixinsdk import Wxpay_server_pub
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.payment_wcpay.models import weixinsdk
_logger = logging.getLogger(__name__)


class weixin(object):
    def set_wcpayconf(self, acquirer):
        wxpayconf = weixinsdk.WxPayConf_pub
        wxpayconf.APPID = acquirer.appid
        wxpayconf.APPSECRET = acquirer.appsecret
        wxpayconf.MCHID = acquirer.mchid
        wxpayconf.KEY = acquirer.key
        wxpayconf.SSLCERT_PATH = acquirer.sslcert_path
        wxpayconf.SSLKEY_PATH = acquirer.sslkey_path
        wxpayconf.CURL_TIMEOUT = acquirer.curl_timeout
        wxpayconf.HTTP_CLIENT = acquirer.http_client
        wxpayconf.SPBILL_CREATE_IP = acquirer.ip_address
        return wxpayconf

    def connect_wcpay(self, cr, uid, tx):
        base_url = request.registry.get('ir.config_parameter').get_param(
            cr, uid, 'web.base.url')
        notify_url = '%s' % urlparse.urljoin(
            base_url, WcpayController._notify_url)
        unifiedorder = weixinsdk.UnifiedOrder_pub()
        unifiedorder.setParameter('out_trade_no', tx.reference)
        unifiedorder.setParameter('body', tx.reference)
        unifiedorder.setParameter(
            'total_fee', '%s' % int(tx.amount * 100))
        unifiedorder.setParameter('notify_url', notify_url)
        unifiedorder.setParameter('trade_type', 'NATIVE')
        result = unifiedorder.getResult()
        return result


class website_sale(website_sale):
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'],
                type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id):
        super(website_sale, self).payment_transaction(acquirer_id)
        tx = request.website.sale_get_transaction()
        acquirer = request.registry.get('payment.acquirer').browse(
            request.cr, request.uid, acquirer_id)
        if acquirer.provider == 'wcpay':
            weixin().set_wcpayconf(acquirer)
            result = weixin().connect_wcpay(request.cr, request.uid, tx)
            if result.get('return_code', None) == 'SUCCESS':
                pay_link = result.get('code_url', None)
                tx.wcpay_txn_paylink = pay_link
            else:
                _logger.warning('wcpay: %s' % result)
        return tx.id


class WcpayController(ReportController):
    _notify_url = '/payment/weixin/notify'

    def kwargs_to_url(self, kwargs):
        res = ['%s=%s' % (args[0], args[1]) for args in kwargs.items()]
        return '&%s' % '&'.join(res)

    @route(['/report/barcode',
            '/report/barcode/<type>/<path:value>'], type='http', auth="user")
    def report_barcode(
            self, type, value, width=600, height=100, humanreadable=0,
            **kwargs):
        """Contoller able to render barcode images thanks to reportlab.
        Samples:
            <img t-att-src="'/report/barcode/QR/%s' % o.name"/>
            <img t-att-src="'/report/barcode/?type=%s&amp;value=%s&amp;
                width=%s&amp;height=%s' %
                ('QR', o.name, 200, 200)"/>

        :param type: Accepted types: 'Codabar', 'Code11', 'Code128', 'EAN13',
        'EAN8', 'Extended39', 'Extended93', 'FIM', 'I2of5', 'MSI', 'POSTNET',
        'QR', 'Standard39', 'Standard93',
        'UPCA', 'USPS_4State'
        :param humanreadable: Accepted values: 0 (default) or 1. 1 will insert
        the readable value at the bottom of the output image
        """
        value += self.kwargs_to_url(kwargs)
        return super(WcpayController, self).report_barcode(
            type, value, width=width, height=height,
            humanreadable=humanreadable)

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from wcpay. """
        return ''

    def wcpay_validate_data(self, xml):
        res = False
        wcpay_back = Wxpay_server_pub()
        wcpay_back.saveData(xml)
        data = wcpay_back.getData()
        if data.get('attach', None):
            # 生成签名时报错
            del data['attach']

        try:
            reference = data.get('out_trade_no')
        except Exception:
            reference = False

        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        if reference:
            tx_ids = request.registry['payment.transaction'].search(
                cr, uid, [('reference', '=', reference)], context=context)
            if tx_ids:
                request.registry['payment.transaction'].browse(
                    cr, uid, tx_ids[0], context=context)
        else:
            # should we create a payment transacation for wcpay
            _logger.warning(
                'wcpay: received wrong reference from wcpay: %s' % (
                    data.get('out_trade_no', '')))
            return res

        if wcpay_back.checkSign():
            _logger.info('wcpay: validated data')
            res = request.registry['payment.transaction'].form_feedback(
                cr, SUPERUSER_ID, data, 'wcpay', context=context)
        else:
            _logger.warning(
                'wcpay: received wrong md5str from wcpay: %s' % (
                    data.get('sign', '')))
        return res

    @http.route('/payment/weixin/notify', type='http', auth='none', methods=[
        'POST'])
    def weixin_notify(self, **post):
        xml = request.httprequest.data
        _logger.info(
            'Beginning wcpay AutoReceive form_feedback with post data %s',
            pprint.pformat(xml))
        res = self.wcpay_validate_data(xml)
        if res:
            return_code = 'SUCCESS'
            return_msg = 'OK'
        else:
            return_code = 'FAIL'
            return_msg = '签名失败'

        wc_return = Wxpay_server_pub()
        wc_return.setReturnParameter('return_code', return_code)
        wc_return.setReturnParameter('return_msg', return_msg)
        return_xml = wc_return.returnXml()
        return return_xml
