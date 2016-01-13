from openerp import api, models, fields
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.tools.float_utils import float_compare
import logging

_logger = logging.getLogger(__name__)


class TxAlipay(models.Model):
    _inherit = 'payment.transaction'

    alipay_txn_tradeno = fields.Char('Transaction Trade Number')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _alipay_form_get_tx_from_data(self, data):
        """ Given a data dict coming from alipay, verify it and find the related
        transaction record. """
        reference = data.get('out_trade_no')
        if not reference:
            error_msg = 'Alipay: received data with missing reference (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx_obj = self.env['payment.transaction'].search(
            [('reference', '=', reference)])
        if not tx_obj or len(tx_obj) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not tx_obj:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        # tx = self.env['payment.transaction'].browse(
        #     tx_ids[0])

        sign_check = self.env['payment.acquirer']._alipay_generate_md5_sign(
            tx_obj.acquirer_id, 'out', data)
        if sign_check != data.get('sign'):
            error_msg = 'alipay: invalid md5str, received %s, computed %s' % (
                data.get('sign'), sign_check)
            _logger.warning(error_msg)
            raise ValidationError(error_msg)
        return tx_obj

    @api.model
    def _alipay_form_get_invalid_parameters(
        self, tx, data
    ):
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
    def _alipay_form_validate(self, tx, data):
        if data.get('trade_status') in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            tx.write({
                'state': 'done',
                'acquirer_reference': data.get('out_trade_no'),
                'alipay_txn_tradeno': data.get('trade_no'),
                'date_validate': data.get('notify_time'),
            })
            return tx
        else:
            error = 'Alipay: feedback error.'
            _logger.info(error)
            tx.write({
                'state': 'error',
                'state_message': error,
            })
            return False
