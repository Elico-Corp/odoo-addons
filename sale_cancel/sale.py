# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm
from openerp import netsvc
import logging

_logger = logging.getLogger(__name__)


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def action_cancel_order_with_moves_not_delivered(
            self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        for sale in self.browse(cr, uid, ids, context=context):
            try:
                for pick in sale.picking_ids:
                    if pick.state != 'cancel':
                        wf_service.trg_validate(
                            uid, 'stock.picking', pick.id, 'button_cancel', cr)
                
                order_ref = context.get('order_ref', False)
                self.action_cancel(cr, uid, [sale.id], context=context)
                self.write(
                    cr, uid,
                    [sale.id],
                    {'client_order_ref': order_ref})
                cr.commit()
            except:
                raise
                _logger.error(
                    '==== #elico-corp: Cancel SO and DO fail! %s====' % (
                        sale.id))
        return True
