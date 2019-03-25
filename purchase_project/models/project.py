# -*- coding: utf-8 -*-
from openerp import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'

    @api.one
    def _compute_purchase_count(self):
        if self and self.id:
            self.purchase_count = self.env['purchase.order'].search_count(
                [('project_id', '=', self.id)])

    purchase_ids = fields.One2many(
        'purchase.order', 'project_id', string='Purchase Order')
    purchase_count = fields.Integer(
        compute='_compute_purchase_count', string="Open Purchases",
    )

    @api.multi
    def action_picking_purchase(self):
        '''
        This function returnns an action that display existing pîcking orders
        of given purchase order ids.
        '''
        self.ensure_one()
        action = self.env.ref('purchase.purchase_rfq').read()[0]

        ctx = eval(action['context'])
        new_domain = "[('project_id', 'in', %s )]" % str(tuple(self._ids))
        if action['domain'] != '[]':
            new_domain = action['domain'][:-1] + "," + new_domain[1:]
        action.update({
            'context': ctx,
            'domain': new_domain
        })

        return action
