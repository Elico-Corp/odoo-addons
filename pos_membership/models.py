# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.osv import fields as old_fields
from openerp.exceptions import Warning

import openerp.addons.decimal_precision as dp


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    membership = fields.Boolean(
        string="Is Membership Journal", default=False)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def _is_there_membership_product(self):
        if self.invoice_line:
            for l in self.invoice_line:
                if l.product_id.membership:
                    return True
        return False


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    def _check_enough_membership_balance(self):
        if self.partner_id:
            if self.partner_id.membership_total_future < self.amount:
                return False
        return True

    @api.multi
    def button_proforma_voucher(self):
        # here, you need to check the supplier invoice, return
        if self.journal_id.membership:
            # check if the invoice is supplier invoices.
            if self._context.get('invoice_type', '').startswith('in_'):
                raise Warning(_('Cannot use VIP card for supplier journal!'))

            # check if there membership product inside.
            if self._context.get('invoice_id'):
                invoice = self.env['account.invoice'].browse(
                    self._context['invoice_id'])
                if invoice._is_there_membership_product():
                    raise Warning(
                        _('Cannot use VIP card for membership product!'))

            # check if there is enough membership balance
            if not self._check_enough_membership_balance():
                raise Warning(_('No enough membership balance!'))
        return super(AccountVoucher, self).button_proforma_voucher()


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def _membership_total_get(
            self, cr, uid, ids, field_names, arg, context=None):
        ctx = context.copy()
        ctx['all_fiscalyear'] = True
        query = self.pool.get('account.move.line')._query_get(
            cr, uid, context=ctx)
        cr.execute("""SELECT l.partner_id, a.type, SUM(l.debit-l.credit)
                      FROM account_move_line l
                      LEFT JOIN account_account a ON (l.account_id=a.id)
                      WHERE a.membership_total IS true
                      AND l.partner_id IN %s
                      AND l.reconcile_id IS NULL
                      AND """ + query + """
                      GROUP BY l.partner_id, a.type
                      """,
                   (tuple(ids),))

        res = {id: {'membership_total': 0, 'membership_total_future': 0}
               for id in ids}
        for pid, type, val in cr.fetchall():
            val = val and float(val) or 0
            res[pid]['membership_total'] = -val
            res[pid]['membership_total_future'] = -val

        # get the total number group by partner.
        # Note: we assume one company only has one VIP journal!!
        # get all the consumed VIP points
        cr.execute('''SELECT bl.partner_id, SUM(bl.amount)
            FROM account_bank_statement_line bl
            LEFT JOIN account_journal aj ON (bl.journal_id = aj.id)
            WHERE bl.pos_statement_id is not NULL
            AND bl.journal_entry_id is NULL
            AND aj.membership IS true
            AND bl.partner_id IN %s
            GROUP BY bl.partner_id
            ''', (tuple(ids),))
        for p_id, amount in cr.fetchall():
            amount = float(amount) or 0.0
            res[p_id].update(
                {'membership_total_future': res[p_id]['membership_total'] -
                    amount})
        # get all the charged VIP points whose POS session hasn't closed yet.
        # get all the paid or invoiced but not done POS order.
        pos_obj = self.pool['pos.order']
        pos_ids = pos_obj.search(
            cr, uid,
            [('state', 'in', ('paid', 'invoiced')),
             ('account_move', '=', False)], context=context)
        for pos in pos_obj.browse(cr, uid, pos_ids, context=context):
            for line in pos.lines:
                if line.product_id.membership:
                    if (not pos.partner_id) or pos.partner_id.id not in ids:
                        continue
                    res[pos.partner_id.id]['membership_total_future'] += \
                        line.price_subtotal_incl
        return res

    _columns = {
        'membership_total': old_fields.function(
            _membership_total_get, multi="mt", string='Total Membership',
            digits_compute=dp.get_precision('Account')),
        'membership_total_future': old_fields.function(
            _membership_total_get, multi="mt",
            string='Future Total Membership',
            digits_compute=dp.get_precision('Account')),
    }
