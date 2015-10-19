# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#     Jon Chow <jon.chow@elico-corp.com>
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
from urllib import urlencode


class account_account(osv.osv):
    _inherit = 'account.invoice'

    def _edi_paypal_url(self, cr, uid, ids, field, arg, context=None):
        res = dict.fromkeys(ids, False)
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type == 'out_invoice' and inv.company_id.paypal_account:

                item_name = "%s Invoice %s" % (
                    inv.company_id.name, inv.number or '')
                item_name = item_name.encode('utf-8')

                params = {
                    "cmd": "_xclick",
                    "business": inv.company_id.paypal_account,
                    "item_name": item_name,
                    "invoice": inv.number,
                    "amount": inv.residual,
                    "currency_code": inv.currency_id.name,
                    "button_subtype": "services",
                    "no_note": "1",
                    "bn": "OpenERP_Invoice_PayNow_" + inv.currency_id.name,
                }
                res[inv.id] = "https://www.paypal.com/cgi-bin/webscr?"\
                    + urlencode(params)
        return res

    _columns = {
        'paypal_url': fields.function(
            _edi_paypal_url, type='char', string='Paypal Url'),
    }
account_account()
