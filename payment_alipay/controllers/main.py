# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http, SUPERUSER_ID
from openerp.http import request
import logging
import pprint
import urlparse
import werkzeug


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
            # Luke create transaction, if payment via email url
            else:
                tx = self.create_transaction_alipay(post)
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

        # Luke modify sign
        md5sign = tx.acquirer_id._alipay_generate_md5_sign(
            tx.acquirer_id, 'out', post)
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
            return 'success'
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

    # Luke if no payment transcation create payment transcation
    def create_transaction_alipay(self, post):
        acquirer = request.env['payment.acquirer'].sudo().search(
            [('provider', '=', 'alipay')])
        sale_order = request.env['sale.order'].sudo().search(
            [('name', '=', post.get('out_trade_no'))])
        if sale_order.pricelist_id:
            currency_id = sale_order.pricelist_id.currency_id.id
        else:
            currency_id = sale_order.company_id.currency_id.id
        param = {
            'reference': post.get('out_trade_no'),
            'acquirer_id': acquirer.id,
            'sale_order_id': sale_order.id,
            'amount': sale_order.amount_total,
            'fees': post.get('total_fee'),
            'partner_id': sale_order.partner_id.id,
            'currency_id': currency_id,
            'partner_country_id': sale_order.partner_id.country_id.id
        }
        tx = request.env['payment.transaction'].sudo().create(param)
        return tx
