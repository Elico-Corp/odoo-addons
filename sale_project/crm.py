# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class crm_lead(orm.Model):
    _inherit = 'crm.lead'
    _columns = {
        'sale_project_id': fields.many2one(
            'sale.project',
            'Sale Project',
            domain="[('partner_id', '=', partner_id)]")
    }

    def on_change_partner(self, cr, uid, ids, partner_id, context=None):
        res = super(crm_lead, self).on_change_partner(
            cr, uid, ids, partner_id, context=context)
        project_pool = self.pool.get('sale.project')
        project_ids = project_pool.search(
            cr, uid, [('partner_id', '=', partner_id)], context=context)
        res['value']['sale_project_id'] = None
        if project_ids:
            res['value']['sale_project_id'] = project_ids[-1]
        return res
