# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
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
############################################################################


from openerp.osv import fields, osv
from openerp.osv import orm, fields, osv

class tenancy_tenant_report(orm.TransientModel):
    
    _name = 'tenancy.tenant.report'
    
    _columns = {
        'start_date' : fields.date('Start date', required=True),
        'end_date' : fields.date('End date', required=True),
        'tenant_id' : fields.many2one('tenant.partner', 'Tenant', required=True)
    }

    def open_tanancy_tenant_gantt_view(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids[0])
        start_date = data['start_date']
        end_date = data['end_date']
        tenant_id = data['tenant_id'][0]
        
        ir_model_data_obj = self.pool.get('ir.model.data')
        wiz_form_id = ir_model_data_obj.get_object_reference(cr,uid,'property_management', 'view_tenancy_gantt')[1]
        
        tenancy_obj = self.pool.get("account.analytic.account")
        tenancy_ids = tenancy_obj.search(cr, uid, [('tenant_id','=',tenant_id),('date_start','>=',start_date),('date_start','<=',end_date)],context=None)
        domain = [('id','in',tenancy_ids)]
        
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'gantt',
            'res_model': 'account.analytic.account',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context':context,
            'domain':domain
            }
    
    def open_tanancy_tenant_tree_view(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids[0])
        start_date = data['start_date']
        end_date = data['end_date']
        tenant_id = data['tenant_id'][0]
        
        ir_model_data_obj = self.pool.get('ir.model.data')
        wiz_form_id = ir_model_data_obj.get_object_reference(cr,uid,'property_management', 'property_tenancy_view_tree')[1]

        
        tenancy_obj = self.pool.get("account.analytic.account")
        tenancy_ids = tenancy_obj.search(cr, uid, [('tenant_id','=',tenant_id),('date_start','>=',start_date),('date_start','<=',end_date)],context=None)
        domain = [('id','in',tenancy_ids)]
        
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'tree',
            'res_model': 'account.analytic.account',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context':context,
            'domain':domain
            }
        
    def print_report(self, cr, uid, ids, data, context=None):
            if context is None:
                context = {}
            data = self.read(cr, uid, ids[0])
            partner_obj = self.pool.get("tenant.partner")
            partner_rec = partner_obj.browse(cr, uid, data['tenant_id'][0])
            data.update({'tenant_name' : partner_rec.name})
            datas = {
                     'ids': [],
                     'model': 'tenant.partner',
                     'form': data
                 }
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'tenancy.detail.tenant',
                    'datas': datas,
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: