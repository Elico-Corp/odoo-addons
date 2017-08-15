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


class tenancy_property_report(orm.TransientModel):
    
    _name = 'tenancy.property.report'
    
    _columns = {
        'start_date' : fields.date('Start date', required=True),
        'end_date' : fields.date('End date', required=True),
        'property_id' : fields.many2one('account.asset.asset','Property', required=True)
    }

    def open_tenancy_by_property_gantt(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids[0])
        start_date = data['start_date']
        end_date = data['end_date']
        property_id = data['property_id'][0]
        
        ir_model_data_obj = self.pool.get('ir.model.data')
        wiz_form_id = ir_model_data_obj.get_object_reference(cr,uid,'property_management', 'view_analytic_gantt')[1]
        tenancy_obj = self.pool.get("account.analytic.account")
        tenancy_ids = tenancy_obj.search(cr, uid, [('property_id','=',property_id),('date_start','>=',start_date),('date_start','<=',end_date)],context=None)
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

    def open_tenancy_by_property_tree(self, cr, uid, ids, context=None):
        
        data = self.read(cr, uid, ids[0])
        start_date = data['start_date']
        end_date = data['end_date']
        property_id = data['property_id'][0]
        
        ir_model_data_obj = self.pool.get('ir.model.data')
        wiz_form_id = ir_model_data_obj.get_object_reference(cr,uid,'property_management', 'property_analytic_view_tree')[1]
        
        tenancy_obj = self.pool.get("account.analytic.account")
        tenancy_ids = tenancy_obj.search(cr, uid, [('property_id','=',property_id),('date_start','>=',start_date),('date_start','<=',end_date)],context=None)
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
            partner_obj = self.pool.get("account.asset.asset")
            partner_rec = partner_obj.browse(cr, uid, data['property_id'][0])
            data.update({'property_name' : partner_rec.name})
            datas = {
                     'ids': [],
                     'model': 'account.asset.asset',
                     'form': data
                 }
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'tenancy.detail',
                    'datas': datas,
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
