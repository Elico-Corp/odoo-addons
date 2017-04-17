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

_logger = logging.getLogger(__name__)


class AlipayController(http.Controller):
    _notify_url = '/payment/alipay/notify'
    _return_url = '/payment/alipay/return'
    _cancel_url = '/payment/alipay/cancel'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from alipay. """
        return ''

    def alipay_validate_data(self, **post):
        res = False

        seller_email = post.get('seller_email')
        if not seller_email:
            return res

        try:
            reference = post.get('out_trade_no')
        except Exception:
            reference = False

        tx = None
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        if reference:
            tx_ids = request.registry['payment.transaction'].search(
                cr, uid, [('reference', '=', reference)], context=context)
            if tx_ids:
                tx = request.registry['payment.transaction'].browse(
                    cr, uid, tx_ids[0], context=context)
        else:
            # LY todo if no payment,
            # should we create a payment transacation for alipay
            _logger.warning(
                'alipay: received wrong reference from alipay: %s' % (
                    post.get('out_trade_no', '')))
            return res

        # LY pay from  portal, tx.acquired may not be alipay,
        # change to alipay acquire to alipay
        self.find_correct_transcation_alipay(tx)
        # todo if no payment transcation create payment transcation

        acquier = request.registry['payment.acquirer']
        md5sign = acquier._alipay_generate_md5_sign(
            tx and tx.acquirer_id, 'out', post)

        if md5sign == post.get('sign', ''):
            _logger.info('alipay: validated data')
            res = request.registry['payment.transaction'].form_feedback(
                cr, SUPERUSER_ID, post, 'alipay', context=context)
        else:
            _logger.warning(
                'alipay: received wrong md5str from alipay: %s' % (
                    post.get('sign', '')))
        return res

    @http.route(
        '/payment/alipay/notify/', type='http', auth='none',
        methods=['POST']
    )
    def alipay_autoreceive(self, **post):
        """ alipay AutoReceive """
        _logger.info(
            'Beginning alipay AutoReceive form_feedback with post data %s',
            pprint.pformat(post))
        res = self.alipay_validate_data(**post)
        if res:
            return 'sucess'
        else:
            return 'error'

    @http.route(
        '/payment/alipay/return/', type='http', auth="none",
        methods=['GET']
    )
    def alipay_return(self, **post):

        cr, uid = request.cr, SUPERUSER_ID
        _logger.info(
            'Beginning alipay Return form_feedback with post data %s',
            pprint.pformat(post))
        base_url = request.registry['ir.config_parameter'].get_param(
            cr, uid, 'web.base.url')
        res = self.alipay_validate_data(**post)

        if res:
            return_url = '%s' % urlparse.urljoin(
                base_url, '/shop/payment/validate')
        else:
            return_url = '%s' % urlparse.urljoin(base_url, '/shop/cart')
        return werkzeug.utils.redirect(return_url)

    # LY
    def find_correct_transcation_alipay(self, payment_transaction):
        try:
            assert payment_transaction.acquire_id.provider == 'alipay'
        except:
            cr, uid = request.cr, SUPERUSER_ID
            acquirer_ids = request.registry['payment.acquirer'].search(
                cr, uid, [('provider', '=', 'alipay')])

            assert len(acquirer_ids) == 1
            payment_transaction.acquirer_id = acquirer_ids[0]

        return
    # LY END
