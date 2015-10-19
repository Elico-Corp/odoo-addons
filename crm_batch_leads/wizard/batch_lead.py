# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-Today Elico Corp. All Rights Reserved.
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

from openerp.osv import fields, orm


class crm_batch_lead(orm.TransientModel):
    _name = "crm.batch.lead"
    _description = "CRM Batch Lead"

    _columns = {
        'stage_id': fields.many2one(
            'crm.case.stage',
            'Stage', required=True)
    }

    def process(self, cr, uid, ids, context=None):
        context = context or {}
        lead_pool = self.pool['crm.lead']
        assert ids, 'Should have at least one instance.'
        batch_wizard = self.browse(cr, uid, ids, context=context)[0]
        stage = batch_wizard.stage_id
        assert stage, 'Must have one stage in the lead batch wizard.'
        active_ids = context.get('active_ids', [])
        lead_pool.write(cr, uid, active_ids, {'stage_id': stage.id})
        action_model, action_id = self.pool.get(
            'ir.model.data').get_object_reference(
                cr, uid, 'crm', 'crm_case_category_act_leads_all')

        action_pool = self.pool.get(action_model)
        action = action_pool.read(cr, uid, action_id, context=context)
        action['domain'] = "[('id','in', [" + ','.join(
            map(str, active_ids)) + "])]"
        action['context'] = "{}"
        return action
