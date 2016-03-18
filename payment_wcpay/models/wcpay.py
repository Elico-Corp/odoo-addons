# -*- coding: utf-8 -*-
import logging
import urlparse
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment_wcpay.controllers.main import WcpayController
from openerp import api, fields, models
from openerp.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class AcquirerWcpay(models.Model):
    _inherit = 'payment.acquirer'

    appid = fields.Char(
        'APPID', required_if_provider='wcpay', help='JSAPI接口中获取openid')
    appsecret = fields.Char(
        'APPSECRET', required_if_provider='wcpay', help='JSAPI接口中获取openid')
    mchid = fields.Char(
        'MCHID', required_if_provider='wcpay', help='商户ID')
    key = fields.Char(
        'KEY', required_if_provider='wcpay', help='商户支付密钥')
    sslcert_path = fields.Char(
        'SSLCERT_PATH - 证书路径', required_if_provider='wcpay',
        help='证书路径,注意应该填写绝对路径')
    sslkey_path = fields.Char(
        'SSLKEY_PATH - 证书路径', required_if_provider='wcpay',
        help='证书路径,注意应该填写绝对路径')
    curl_timeout = fields.Char(
        'CURL_TIMEOUT - curl超时', required_if_provider='wcpay', default=30)
    http_client = fields.Selection(
        [('CURL', 'CURL'), ('URLLIB', 'URLLIB')],
        'HTTP_CLIENT - HTTP客户端', required_if_provider='wcpay', default='CURL')
    ip_address = fields.Char(
        'IP Address', required_if_provider='wcpay', default='127.0.0.1')
    logistics_type = fields.Char(
        'Logistics Type', required_if_provider='wcpay')
    logistics_fee = fields.Char(
        'Logistics Fee', required_if_provider='wcpay')
    logistics_payment = fields.Char(
        'Logistics Payment', required_if_provider='wcpay')
    service = fields.Selection(
        [('create_direct_pay_by_user',
          'create_direct_pay_by_user'),
         ('create_partner_trade_by_buyer',
          'create_partner_trade_by_buyer'), ],
        'Payment Type',
        default='create_direct_pay_by_user',
        required_if_provider='wcpay'
    )

    @api.model
    def _get_wcpay_urls(self, environment):
        """ Wcpay URLs
        """
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        wcpay_form_url = '%s' % urlparse.urljoin(
            base_url, '/shop/confirmation')
        return {
            'wcpay_form_url': wcpay_form_url,
        }

    @api.model
    def _get_providers(self):
        providers = super(AcquirerWcpay, self)._get_providers()
        providers.append(['wcpay', 'Wechat Pay'])
        return providers

    @api.multi
    def wcpay_form_generate_values(
        self, partner_values, tx_values
    ):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        acquirer = self.browse(self.id)

        wcpay_tx_values = dict(tx_values)
        wcpay_tx_values.update({
            'total_fee': tx_values['amount'],
            'out_trade_no': tx_values['reference'],
            'payment_type': '1',
            'service': acquirer.service,
            '_input_charset': '',
            'sign_type': 'MD5',
            'subject': tx_values['reference'],
            'price': tx_values['amount'],
            'quantity': 1,
            'logistics_fee': acquirer.logistics_fee,
            'logistics_payment': acquirer.logistics_payment,
            'logistics_type': acquirer.logistics_type,
            'notify_url': '%s' % urlparse.urljoin(
                base_url, WcpayController._notify_url),
            'sign': ''
        })
        return partner_values, wcpay_tx_values

    @api.multi
    def wcpay_get_form_action_url(self):
        self.ensure_one()
        return self._get_wcpay_urls(self.environment)['wcpay_form_url']


class TxWcPay(models.Model):
    _inherit = 'payment.transaction'

    wcpay_txn_tradeno = fields.Char('Transaction Trade Number')
    wcpay_txn_paylink = fields.Char('Transaction Pay Link')

    @api.model
    def _wcpay_form_get_tx_from_data(self, data):
        """ Given a data dict coming from wcpay, verify it and find the related
        transaction record. """
        reference = data.get('out_trade_no')
        if not reference:
            error_msg = 'Wcpay: received data with missing reference (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx_ids = self.pool['payment.transaction'].search(
            [('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'wcpay: received data for reference %s' % (reference)
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.pool['payment.transaction'].browse(tx_ids[0])
        return tx

    @api.model
    def _wcpay_form_get_invalid_parameters(
            self, tx, data):
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

    @api.model
    def _wcpay_form_validate(self, tx, data):
        if data.get('trade_status') in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            tx.write({
                'state': 'done',
                'acquirer_reference': data.get('out_trade_no'),
                'wcpay_txn_tradeno': data.get('trade_no'),
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
