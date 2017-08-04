# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields
from collections import Iterable


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'has_prepaid': fields.boolean('Has been Prepaid', readonly=True),

    }

    _defaults = {
        'has_prepaid': False
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['has_prepaid'] = False
        return super(sale_order, self).copy(cr, uid, id,
                                            default, context=context)

    def automatic_payment(self, cr, uid, ids, amount=None, context=None):
        """ If this quotation hasn't been prepaid
        Create the payment entries to pay a sale order, respecting
        the payment terms.
        If no amount is defined, it will pay the residual amount of the sale
        order.
        Otherwise do nothing.
        rewrite the function in sale_automatic_payment"""
        if not ids:
            return False
        if isinstance(ids, Iterable):
            assert len(ids) == 1, "one sale order at a time can be paid"
            ids = ids[0]
        sale = self.browse(cr, uid, ids, context=context)
        if sale.has_prepaid is False:
            return super(sale_order, self).automatic_payment(
                cr, uid, ids, amount=amount, context=context)
        return True

    def _prepare_payment_move_line(self, cr, uid, move_name, sale, journal,
                                   period, amount, date, context=None):
        """ """
        debit_line, credit_line = super(
            sale_order, self)._prepare_payment_move_line(
            cr, uid, move_name, sale, journal, period, amount,
            date, context=context)
        partner_obj = self.pool.get('res.partner')
        partner_id = sale.partner_invoice_id or\
            sale.partner_id or False
        partner = partner_obj._find_accounting_partner(partner_id)
        debit_line['partner_id'] = partner.id
        credit_line['partner_id'] = partner.id
        return debit_line, credit_line
