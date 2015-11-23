# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Siyuan Gu
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

from openerp import models, fields, api, _


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
