# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _get_reference_type(self, cr, uid, context=None):
        return [('none', _('Free Reference'))] #,
    
    _columns = {
        'supplier_invoice_number': fields.char('Officer Fapiao', size=64, help="The reference of this invoice as provided by the supplier."),
        'fapiao_date': fields.date('Fapiao Date', ),
        'partner_ref': fields.related('partner_id','ref',type='char', size=64, string='Partner Ref'),
        'reference_type': fields.selection(_get_reference_type, 'Payment Reference',
            required=True, readonly=True, states={'draft':[('readonly',False)]}),
    }
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _amount_line_with_tax(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id, force_excluded=True)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res
    
    _columns = {
        'amount_subtotal': fields.function(_amount_line_with_tax, string='Amount (Inc. Tax)', type='float', digits_compute=dp.get_precision('Account')),
        'partner_ref': fields.related(
                    'partner_id', 'ref',
                    type='char', size=64,relation='res.partner',
                    string='Partner Ref',select=1),
        'type': fields.related(
                    'invoice_id', 'type',
                    type='char', size=64,relation='account.invoice',
                    string='Type'),
        'number': fields.related(
                    'invoice_id', 'number',
                    type='char', size=64,relation='account.invoice',
                    string='Number',select=1),
        'supplier_invoice_number': fields.related(
                    'invoice_id', 'supplier_invoice_number',
                    type='char', size=64,relation='account.invoice',
                    string='Supplier Inv Ref',select=1),
        'date_invoice': fields.related(
                    'invoice_id', 'date_invoice',
                    type='date', relation='account.invoice',
                    string='Date Invoice',select=1),
        'state': fields.related(
                    'invoice_id', 'state',
                    type='char', size=16,relation='account.invoice',
                    string='State'),
        'reference': fields.related(
                    'invoice_id', 'reference',
                    type='char', size=16,relation='account.invoice',
                    string='Reference'),
    }
account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
