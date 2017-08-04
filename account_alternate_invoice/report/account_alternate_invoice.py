# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

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

