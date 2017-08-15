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

class operational_costs_per_property(orm.TransientModel):
    
    _name = 'operational.costs.per.property'
    
    _columns = {
         'type':fields.selection([('period','Period'),('property','Property'),('property_type','Property Type')],'Select'),
        'start_date' : fields.date('Start date', required=True),
        'end_date' : fields.date('End date', required=True),
        'property':fields.many2one('account.asset.asset', 'Property'),
        'property_type':fields.many2one('property.type', 'Property Type'),
    }
    

    def open_operational_costs_per_property_graph(self, cr, uid, ids, context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')
        wiz_form_id = ir_model_data_obj.get_object_reference(cr,uid,'property_management', 'view_operational_cost_graph')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'graph',
            'res_model': 'account.asset.asset',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context':context,
            }

