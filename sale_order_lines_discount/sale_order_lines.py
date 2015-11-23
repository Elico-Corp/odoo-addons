# -*- encoding: utf-8 -*-
# __author__ = xia.fajin@elico-corp.com
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from openerp import models, fields, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
import math

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _name = 'sale.order'

    _columns = {
        'all_discounts': fields.float('All order lines discount', required=True, help='Change all order lines discount.'),
    }

    def update_discount_lines(self, cr, uid, ids, context=None):
        if context.get('all_discounts', 0) < 100 and context.get('all_discounts', 0) >= 0:
            lines = self.browse(cr, uid, ids, context=context).order_line
            lines.write({'discount':context['all_discounts']})
            return             
        else:
            raise osv.except_osv(_('Error!'),_("Your discount value is out of vlaues,it's value between 0 and 100,but 100 except."))

