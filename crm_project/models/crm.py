# -*- coding: utf-8 -*-
from openerp import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.one
    def _compute_project_count(self):
        ctx = self._context.copy()
        ctx['active_test'] = False
        self.project_count = self.env['project.project'].search_count(
            [('opportunity_id', 'in', self._ids)], context=ctx)

    project_line_ids = fields.One2many(
        'project.project', 'opportunity_id', 'Projects Lines')
    project_count = fields.Integer(
        compute='_compute_project_count', string="Open Projects")

    @api.multi
    def action_picking(self):
        '''
        This function returnns an action that display existing pîcking orders
         of given purchase order ids.
        '''
        self.ensure_one()
        action = self.env.ref('project.open_view_project_all').read()[0]

        ctx = eval(action['context'])
        new_domain = "[('opportunity_id', 'in', %s )]" % str(tuple(self._ids))
        if action['domain'] != '[]':
            new_domain = action['domain'][:-1] + "," + new_domain[1:]
        action.update({
            'context': ctx,
            'domain': new_domain
        })
        return action
