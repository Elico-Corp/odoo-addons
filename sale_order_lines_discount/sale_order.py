# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.osv import osv
from openerp.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    all_discounts = fields.Float(
        'All order lines discount',
        required=True,
        default=0,
        help='Change all order lines discount.')

    @api.multi
    def update_discount_lines(self):
        for sale_obj in self:
            all_discounts = sale_obj.all_discounts
            if all_discounts < 100 and all_discounts >= 0:
                lines = sale_obj.order_line
                lines.write({'discount': all_discounts})
                return
            else:
                raise osv.except_osv(
                    _('Error!'),
                    _("""Your discount value is out of values,
                        it's value between 0 and 100,but 100 except."""))
