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
    
    
        

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
  