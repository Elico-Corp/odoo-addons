# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp


class account_invoice_line(osv.Model):
    _inherit = "account.invoice.line"

    def _amount_line_with_tax(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(
                cr, uid, line.invoice_line_tax_id, price, line.quantity,
                product=line.product_id, partner=line.invoice_id.partner_id,
                force_excluded=True)
            res[line.id] = taxes['total_included']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'amount_subtotal': fields.function(_amount_line_with_tax, string='Amount (Inc. Tax)', type='float', digits_compute=dp.get_precision('Account')),
    }
