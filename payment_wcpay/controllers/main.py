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
import pprint
import werkzeug
import urlparse
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.web.http import route
from openerp.addons.report.controllers.main import ReportController
from openerp.addons.payment_wcpay.models.wzhifuSDK import Wxpay_server_pub
_logger = logging.getLogger(__name__)


class AlipayController(ReportController):
    _notify_url = '/payment/wcpay/notify'
    _return_url = '/payment/wcpay/return'
    _cancel_url = '/payment/wcpay/cancel'

    def kwargs_to_url(self, kwargs):
        res = ['%s=%s' % (args[0], args[1]) for args in kwargs.items()]
        return '&%s' % '&'.join(res)

    @route(
        ['/report/barcode', '/report/barcode/<type>/<path:value>'],
        type='http', auth="user")
    def report_barcode(
            self, type, value, width=600, height=100,
            humanreadable=0, **kwargs):
        value += self.kwargs_to_url(kwargs)
        return super(AlipayController, self).report_barcode(
            type, value, width=width, height=height,
            humanreadable=humanreadable)

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from wcpay. """
        return ''

    def wcpay_validate_data(self, post):
        res = False
        # seller_email = post.get('seller_email')
        # if not seller_email:
        #     return res
        xml = post
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

        # tx = None
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        if reference:
            tx_ids = request.registry['payment.transaction'].search(
                cr, uid, [('reference', '=', reference)], context=context)
            if tx_ids:
                request.registry['payment.transaction'].browse(
                    cr, uid, tx_ids[0], context=context)
        else:
            # LY todo if no payment,
            # should we create a payment transacation for wcpay
            _logger.warning(
                'wcpay: received wrong reference from wcpay: %s' % (
                    data.get('out_trade_no', '')))
            return res

        # LY pay from  portal, tx.acquired may not be wcpay,
        # change to wcpay acquire to wcpay
        # self.find_correct_transcation_wcpay(tx)
        # todo if no payment transcation create payment transcation

        # acquier = request.registry['payment.acquirer']
        # md5sign = acquier._wcpay_generate_md5_sign(
        #     tx and tx.acquirer_id, 'out', post)

        # if md5sign == post.get('sign', ''):
        if wcpay_back.checkSign():
            _logger.info('wcpay: validated data')
            res = request.registry['payment.transaction'].form_feedback(
                cr, SUPERUSER_ID, data, 'wcpay', context=context)
        else:
            _logger.warning(
                'wcpay: received wrong md5str from wcpay: %s' % (
                    data.get('sign', '')))
        return res

    @http.route(
        '/payment/wcpay/notify/', type='http', auth='none',
        methods=['POST']
    )
    def wcpay_autoreceive(self, **post):
        """ wcpay AutoReceive """
        _logger.info(
            'Beginning wcpay AutoReceive form_feedback with post data %s',
            pprint.pformat(post))
        res = self.wcpay_validate_data(post)
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

    @http.route(
        '/payment/wcpay/return/', type='http', auth="none",
        methods=['GET']
    )
    def wcpay_return(self, **post):
        cr, uid = request.cr, SUPERUSER_ID
        _logger.info(
            'Beginning wcpay Return form_feedback with post data %s',
            pprint.pformat(post))
        base_url = request.registry['ir.config_parameter'].get_param(
            cr, uid, 'web.base.url')
        res = self.wcpay_validate_data(**post)

        if res:
            return_url = '%s' % urlparse.urljoin(
                base_url, '/shop/payment/validate')
        else:
            return_url = '%s' % urlparse.urljoin(base_url, '/shop/cart')
        return werkzeug.utils.redirect(return_url)

    # LY
    def find_correct_transcation_wcpay(self, payment_transaction):
        try:
            assert payment_transaction.acquire_id.provider == 'wcpay'
        except:
            cr, uid = request.cr, SUPERUSER_ID
            acquirer_ids = request.registry['payment.acquirer'].search(
                cr, uid, [('provider', '=', 'wcpay')])

            assert len(acquirer_ids) == 1
            payment_transaction.acquirer_id = acquirer_ids[0]

        return
    # LY END
