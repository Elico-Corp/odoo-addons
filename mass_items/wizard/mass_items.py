# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _


class MassItems(models.TransientModel):
    _name = 'mass.items'
    _description = 'Add Items'

    product_ids = fields.Many2many('product.product', string='Product')

    def _get_ids(self):
        return [product.id for product in self.product_ids]

    @api.one
    def cancel_sheet(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def adjust_quantities(self):
        active_model = self._context['active_model']

        if not self.product_ids:
            return {'type': 'ir.actions.act_window_close'}

        # there are duplicated products in the lines.
        # create the context
        ctx = {
            'parent_id': self._context.get('active_id'),
            'parent_model': active_model,
            'product_ids': self._get_ids()
        }

        return {
            'name': _('Adjust Quantity'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form,tree',
            'res_model': 'mass.items.quantities',
            'target': 'new',
            'context': ctx,
        }
