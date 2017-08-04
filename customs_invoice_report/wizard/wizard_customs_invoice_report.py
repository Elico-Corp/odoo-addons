# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import fields, osv


class  wizard_customs_invoice_report(osv.osv_memory):
    _name = 'wizard.customs.invoice.report'
    _columns = {
        'name': fields.char('name', size=32),
        'customs_total': fields.float('Customer Total',),
    }
    
    def action_print(self, cr, uid, ids, context=None):
        
        wizard = self.browse(cr, uid, ids[0], context=None)
        invoice_ids = context.get('active_ids', False)
        
        datas = {
            'model': 'account.invoice',
            'ids': invoice_ids,
         }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'customs_invoice_report',
            'datas': datas,
            'context': {'invoice_ids': invoice_ids, 'customs_total': wizard.customs_total},
        }
    
    
        


  