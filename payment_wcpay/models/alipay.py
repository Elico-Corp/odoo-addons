# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Chen Rong <chen.rong@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import urlparse
from hashlib import md5
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment_wcpay.controllers.main import AlipayController
from openerp.osv import osv, fields
from openerp.tools.float_utils import float_compare
from openerp import SUPERUSER_ID
from . import wzhifuSDK

_logger = logging.getLogger(__name__)


class AcquirerAlipay(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_wcpay_urls(self, cr, uid, environment, context=None):
        """ Alipay URLs
        """
        return {
            'alipay_form_url':
                'https://api.mch.weixin.qq.com/pay/unifiedorder',
        }

    def _get_providers(self, cr, uid, context=None):
        providers = super(AcquirerAlipay, self)._get_providers(
            cr, uid, context=context)
        providers.append(['wcpay', 'Wechat Pay'])
        return providers

    _columns = {
        'appid': fields.char(
            'APPID - 微信公众号身份标识', required_if_provider='wcpay'),
        'appsecret': fields.char(
            'APPSECRET - JSAPI接口中获取openid', required_if_provider='wcpay'),
        'mchid': fields.char(
            'MCHID - 受理商ID', required_if_provider='wcpay'),
        'key': fields.char(
            'KEY - 商户支付密钥Key', required_if_provider='wcpay'),
        'notify_url': fields.char(
            'NOTIFY_URL - 异步通知url', required_if_provider='wcpay'),
        'js_api_call_url': fields.char(
            'JS_API_CALL_URL - JSAPI路径', required_if_provider='wcpay',
            help='获取access_token过程中的跳转uri,通过跳转将code传入jsapi支付页面 '),
        'sslcert_path': fields.char(
            'SSLCERT_PATH - 证书路径', required_if_provider='wcpay',
            help='证书路径,注意应该填写绝对路径'),
        'sslkey_path': fields.char(
            'SSLKEY_PATH - 证书路径', required_if_provider='wcpay',
            help='证书路径,注意应该填写绝对路径'),
        'curl_timeout': fields.char(
            'CURL_TIMEOUT - curl超时', required_if_provider='wcpay', default=30),
        'http_client': fields.selection(
            [('CURL', 'CURL'),
             ('URLLIB', 'URLLIB'),
             ],
            'HTTP_CLIENT - HTTP客户端', required_if_provider='wcpay',
            default='CURL'),

        'alipay_pid': fields.char('PID', required_if_provider='wcpay'),
        'alipay_key': fields.char('Key', required_if_provider='wcpay'),
        'alipay_seller_email': fields.char(
            'Seller Email', required_if_provider='wcpay'),
        'logistics_type': fields.char(
            'Logistics Type', required_if_provider='wcpay'),
        'logistics_fee': fields.char(
            'Logistics Fee', required_if_provider='wcpay'),
        'logistics_payment': fields.char(
            'Logistics Payment', required_if_provider='wcpay'),
        'service': fields.selection(
            [('create_direct_pay_by_user',
              'create_direct_pay_by_user'),
             ('create_partner_trade_by_buyer',
              'create_partner_trade_by_buyer'), ],
            'Payment Type',
            default='create_direct_pay_by_user',
            required_if_provider='wcpay'
        ),
    }

    def _check_payment_type(self, cr, uid, ids, context=None):
        payment_ids = self.read(
            cr, uid, ids, ['service', 'provider'], context=context)
        for payment in payment_ids:
            if payment['provider'] == 'wcpay' and not payment['service']:
                return False
        return True

    _constraints = [
        (
            _check_payment_type,
            'Payment type is NULL.', ['service']
        )
    ]

    def _wcpay_generate_md5_sign(self, acquirer, inout, values):
        """ Generate the md5sign for incoming or outgoing communications.

        :param browse acquirer: the payment.acquirer browse record. It should
                                have a md5key in shaky out
        :param string inout: 'in' (openerp contacting wcpay) or 'out' (wcpay
                             contacting openerp).
        :param dict values: transaction values

        :return string: md5sign
        """
        assert inout in ('in', 'out')
        assert acquirer.provider == 'wcpay'

        alipay_key = acquirer.alipay_key

        if inout == 'out':
            keys = ['buyer_email', 'buyer_id', 'exterface', 'is_success',
                    'notify_id', 'notify_time', 'notify_type', 'out_trade_no',
                    'payment_type', 'seller_email', 'seller_id', 'subject',
                    'total_fee', 'trade_no', 'trade_status']
            src = '&'.join(
                ['%s=%s' % (key, value) for key, value in sorted(
                    values.items()) if key in keys]) + alipay_key
        else:
            if values['service'] == 'create_direct_pay_by_user':
                keys = ['return_url', 'notify_url', '_input_charset',
                        'partner', 'payment_type', 'seller_email',
                        'service', 'out_trade_no', 'subject', 'total_fee']
                src = '&'.join(
                    ['%s=%s' % (key, value) for key, value in sorted(
                        values.items()) if key in keys]) + alipay_key
            elif values['service'] == 'create_partner_trade_by_buyer':
                keys = ['return_url', 'notify_url', 'logistics_type',
                        'logistics_fee', 'logistics_payment', 'price',
                        'quantity', '_input_charset', 'partner',
                        'payment_type', 'seller_email', 'service',
                        'out_trade_no', 'subject']
                src = '&'.join(
                    ['%s=%s' % (key, value) for key, value in sorted(
                        values.items()) if key in keys]) + alipay_key
        return md5(src.encode('utf-8')).hexdigest()

    def wcpay_form_generate_values(
        self, cr, uid, id, partner_values, tx_values,
        context=None
    ):
        base_url = self.pool['ir.config_parameter'].get_param(
            cr, SUPERUSER_ID, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        # wx_pay_conf = self.set_wx_pay_conf(acquirer)
        self.set_wx_pay_conf(acquirer)
        # wc_Jsapi = wcJsapi_pub(wx_pay_conf.CURL_TIMEOUT)

        reusult = self.set_unified_order_pub(tx_values)
        code_url = reusult.get('code_url', None)
        # native_link = self.get_native_link(code_url)
        native_link = code_url

        wcpay_tx_values = dict(tx_values)
        wcpay_tx_values.update({
            'total_fee': tx_values['amount'],
            'out_trade_no': tx_values['reference'],
            'partner': acquirer.alipay_pid,
            'payment_type': '1',
            'service': acquirer.service,
            'seller_email': acquirer.alipay_seller_email,
            '_input_charset': '',
            'sign_type': 'MD5',
            'subject': tx_values['reference'],
            'price': tx_values['amount'],
            'quantity': '1',
            'logistics_fee': acquirer.logistics_fee,
            'logistics_payment': acquirer.logistics_payment,
            'logistics_type': acquirer.logistics_type,
            'return_url': '%s' % urlparse.urljoin(
                base_url, AlipayController._return_url),
            'notify_url': '%s' % urlparse.urljoin(
                base_url, AlipayController._notify_url),
            'cancel_return': '%s' % urlparse.urljoin(
                base_url, AlipayController._cancel_url),
            'native_link': native_link,
        })
        wcpay_tx_values['sign'] = self._wcpay_generate_md5_sign(
            acquirer, 'in', wcpay_tx_values)
        return partner_values, wcpay_tx_values

    def wcpay_get_form_action_url(self, cr, uid, id, context=None):
        acquirer = self.browse(cr, uid, id, context=context)
        return self._get_wcpay_urls(
            cr, uid, acquirer.environment, context=context)['alipay_form_url']

    def set_wx_pay_conf(self, acquirer):
        wx_pay_conf = wzhifuSDK.wx_pay_conf()
        wx_pay_conf.APPID = acquirer.appid
        wx_pay_conf.APPSECRET = acquirer.appsecret
        wx_pay_conf.MCHID = acquirer.mchid
        wx_pay_conf.KEY = acquirer.key
        wx_pay_conf.NOTIFY_URL = acquirer.notify_url
        wx_pay_conf.JS_API_CALL_URL = acquirer.js_api_call_url
        wx_pay_conf.SSLCERT_PATH = acquirer.sslcert_path
        wx_pay_conf.SSLKEY_PATH = acquirer.sslkey_path
        wx_pay_conf.CURL_TIMEOUT = acquirer.curl_timeout
        wx_pay_conf.HTTP_CLIENT = acquirer.http_client
        return wx_pay_conf

    def set_unified_order_pub(self, tx_values):
        unified_order_pub = wzhifuSDK.unified_order_pub()
        unified_order_pub.setParameter('out_trade_no', tx_values['reference'])
        unified_order_pub.setParameter('body', tx_values['reference'])
        unified_order_pub.setParameter(
            'total_fee', '%s' % int(tx_values['amount'] * 100))
        unified_order_pub.setParameter('notify_url', '/payment/wcpay/notify')
        unified_order_pub.setParameter('trade_type', 'NATIVE')
        reusult = unified_order_pub.getResult()
        return reusult

    def get_native_link(self, code_url):
        link = ''
        if code_url:
            native_link_pub = wzhifuSDK.native_link_pub()
            native_link_pub.setParameter('code_url', code_url)
            native_link_pub.setParameter('product_id', '11111')
            link = native_link_pub.getUrl()
        return link


class TxAlipay(osv.Model):
    _inherit = 'payment.transaction'

    _columns = {
        'alipay_txn_tradeno': fields.char('Transaction Trade Number'),
    }

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def _wcpay_form_get_tx_from_data(self, cr, uid, data, context=None):
        """ Given a data dict coming from wcpay, verify it and find the related
        transaction record. """
        reference = data.get('out_trade_no')
        if not reference:
            error_msg = 'Alipay: received data with missing reference (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx_ids = self.pool['payment.transaction'].search(
            cr, uid, [('reference', '=', reference)], context=context)
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.pool['payment.transaction'].browse(
            cr, uid, tx_ids[0], context=context)

        sign_check = self.pool['payment.acquirer']._wcpay_generate_md5_sign(
            tx.acquirer_id, 'out', data)
        if sign_check != data.get('sign'):
            error_msg = 'wcpay: invalid md5str, received %s, computed %s' % (
                data.get('sign'), sign_check)
            _logger.warning(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _wcpay_form_get_invalid_parameters(
            self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        diff = data.get('out_trade_no') != tx.acquirer_reference
        if tx.acquirer_reference and diff:
            invalid_parameters.append((
                'Transaction Id',
                data.get('out_trade_no'),
                tx.acquirer_reference))

        total_fee = float(data.get('total_fee', '0.0'))
        if float_compare(total_fee, tx.amount, 2) != 0:
            invalid_parameters.append(
                ('Amount', data.get('total_fee'), '%.2f' % tx.amount))

        return invalid_parameters

    def _wcpay_form_validate(self, cr, uid, tx, data, context=None):
        if data.get('trade_status') in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            tx.write({
                'state': 'done',
                'acquirer_reference': data.get('out_trade_no'),
                'alipay_txn_tradeno': data.get('trade_no'),
                'date_validate': data.get('notify_time'),
            })
            return True
        else:
            error = 'Wcpay: feedback error.'
            _logger.info(error)
            tx.write({
                'state': 'error',
                'state_message': error,
            })
            return False
