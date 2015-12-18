# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv


class AccountAccount(osv.osv):
    _inherit = "account.account"

    _columns = {
        'membership_total': fields.boolean(
            'Membership account', default=False),
    }


class ResPartner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def _credit_debit_get(self, cr, uid, ids, field_names, arg, context=None):
        ctx = context.copy()
        ctx['all_fiscalyear'] = True
        query = self.pool.get('account.move.line')._query_get(
            cr, uid, context=ctx)
        cr.execute("""SELECT l.partner_id, a.type, SUM(l.debit-l.credit)
                      FROM account_move_line l
                      LEFT JOIN account_account a ON (l.account_id=a.id)
                      WHERE a.type IN ('receivable','payable')
                      AND a.membership_total IS not true
                      AND l.partner_id IN %s
                      AND l.reconcile_id IS NULL
                      AND """ + query + """
                      GROUP BY l.partner_id, a.type
                      """,
                   (tuple(ids),))
        maps = {'receivable': 'credit', 'payable': 'debit'}
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for pid, type, val in cr.fetchall():
            if val is None:
                val = 0
            res[pid][maps[type]] = (type == 'receivable') and val or -val
        return res

    def _credit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(
            cr, uid, obj, name, 'receivable', args, context=context)

    def _debit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(
            cr, uid, obj, name, 'payable', args, context=context)

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

        res = {}.fromkeys(ids, 0)

        for pid, type, val in cr.fetchall():
            if val is None:
                val = 0
            res[pid] = -val
        return res

    _columns = {
        'membership_total': fields.function(
            _membership_total_get, string='Total Membership'),
        'credit': fields.function(
            _credit_debit_get, string='Total Receivable',
            fnct_search=_credit_search,
            multi='dc', help="Total amount this customer owes you."
        ),
        'debit': fields.function(
            _credit_debit_get, string='Total Payable',
            fnct_search=_debit_search,
            multi='dc', help="Total amount you have to pay to this supplier."
        ),
    }
