# -*- coding: utf-8 -*-
from openerp import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'

    @api.one
    def _compute_order_count(self):
        if self and self.id:
            self.order_count = self.env['sale.order'].search_count(
                [('crm_project_id', '=', self.id)])

    opportunity_id = fields.Many2one(
        'crm.lead', string='Opportunity Reference')
    order_ids = fields.One2many(
        'sale.order', 'crm_project_id', string='Sale Order')
    order_count = fields.Integer(
        compute='_compute_order_count', string="Open Orders")

    @api.multi
    def action_picking_order(self):
        '''
        This function returnns an action that display existing pîcking orders
        of given purchase order ids.
        '''
        self.ensure_one()
        action = self.env.ref('sale.action_quotations').read()[0]

        ctx = eval(action['context'])
        new_domain = "[('crm_project_id', 'in', %s )]" % str(tuple(self._ids))
        if action['domain'] != '[]':
            new_domain = action['domain'][:-1] + "," + new_domain[1:]
        action.update({
            'context': ctx,
            'domain': new_domain
        })
        return action
