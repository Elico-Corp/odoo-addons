# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from openerp.report import report_sxw

class account_alternate_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_alternate_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_customs_des': self._get_customs_des,
            
        })
        
    def _get_customs_des(self,line,context=None):
        res = ''
        product = line.product_id
        default_code = product.default_code
        default_code = default_code and '[' + default_code + '] ' or ''
        desc = product.customs_description or product.name
        hs = product.hs_code and 'HS Code: ' + product.hs_code or ''
        res = default_code + desc + '\n' + hs
        return res
        
        
            
report_sxw.report_sxw(
    'report.account.alternate.invoice',
    'account.invoice',
    'extra_addons/account_alternate_invoice/report/account_alternate_invoice.rml',
    parser=account_alternate_invoice
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
