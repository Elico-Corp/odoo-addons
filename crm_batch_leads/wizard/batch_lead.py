# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class CrmBatchLead(orm.TransientModel):
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
