# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.osv import osv, fields
from openerp.tools.translate import _


class AccountVoucher(osv.osv):
    _inherit = "account.voucher"

    _columns = {
        'purchase_id': fields.many2one(
            'purchase.order',
            'Purchase Order',
            domain=[('invoiced', '=', False)],
            ondelete='set null'),
        'use_prepayment_account': fields.boolean(
            'Use Prepayment account',
            help="Check this if you want to input a prepayment \
            on the prepayment accounts."),
        'sale_id': fields.many2one(
            'sale.order',
            'Sale Order',
            domain=[('invoiced', '=', False)],
            ondelete='set null'),
    }
    _defaults = {'use_prepayment_account': False, }

    def onchange_sale_id(self, cr, uid, ids, sale_id):
        res = {}
        if not sale_id:
            return res
        amount = 0
        so_obj = self.pool.get('sale.order')
        so = so_obj.browse(cr, uid, sale_id)
        if so.invoiced:
            res['warning'] = {'title': _('Warning!'),
                              'message': _('Selected Sale Order was paid.')}
        for invoice in so.invoice_ids:
            amount = invoice.residual
        res['value'] = {'partner_id': so.partner_id.id, 'amount': amount}
        return res

    def onchange_purchase_id(self, cr, uid, ids, purchase_id):
        res = {}
        if not purchase_id:
            return res
        amount = 0
        po_obj = self.pool.get('purchase.order')
        po = po_obj.browse(cr, uid, purchase_id)
        if po.invoiced:
            res['warning'] = {'title': _('Warning!'),
                              'message': _('Selected Purchase Order was \
                                paid.')}

        for invoice in po.invoice_ids:
            amount = invoice.residual
        res['value'] = {'partner_id': po.partner_id.id, 'amount': amount}
        return res

    def onchange_prepayment_account(
            self, cr, uid, ids, use_prepayment_account):
        res = {}
        if not use_prepayment_account:
            return res

        res['value'] = {'line_cr_ids': [], 'line_dr_ids': [], 'line_ids': []}
        return res

    def writeoff_move_line_get(self,
                               cr,
                               uid,
                               voucher_id,
                               line_total,
                               move_id,
                               name,
                               company_currency,
                               current_currency,
                               context=None):
        line_vals = super(AccountVoucher, self).writeoff_move_line_get(
            cr,
            uid,
            voucher_id,
            line_total,
            move_id,
            name,
            company_currency,
            current_currency,
            context=context)
        if line_vals:
            account_id = False
            voucher_brw = self.pool.get('account.voucher').browse(
                cr, uid, voucher_id, context)
            if voucher_brw.use_prepayment_account:
                if voucher_brw.payment_option == 'with_writeoff':
                    account_id = voucher_brw.writeoff_acc_id.id
                elif voucher_brw.type in ('sale', 'receipt'):
                    if not voucher_brw.partner_id.\
                            property_account_prereceivable:
                        raise osv.except_osv(
                            _('Unable to validate payment !'),
                            _('Please configure the partner Prereceivable \
                                Account at first!'))
                    account_id = voucher_brw.partner_id.\
                        property_account_prereceivable.id
                else:
                    if not voucher_brw.partner_id.property_account_prepayable:
                        raise osv.except_osv(
                            _('Unable to validate payment !'),
                            _('Please configure the partner Prepayable Account\
                                at first!'))
                    account_id = voucher_brw.partner_id.\
                        property_account_prepayable.id
                if account_id:
                    line_vals['account_id'] = account_id
        return line_vals


AccountVoucher()
