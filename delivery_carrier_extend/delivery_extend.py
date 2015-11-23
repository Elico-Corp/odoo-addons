# -*- encoding: utf-8 -*-
# __author__ = xia.fajin@elico-corp.com
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

import logging
import time
from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class delivery_carrier(osv.osv):
    '''
    Add new filed to record the percentage of the total price if  pay by paypal.
    '''
    _inherit = "delivery.carrier"
    _name = "delivery.carrier"

    _columns = {
        'percentage': fields.float('The Percentage  of price', required=True, help='The percentage of the total price.Value between 0~100.'),
    }

class delivery_grid(osv.osv):
    '''
    Inherit  the delivery_grid function to change the transport fees.
    '''
    _inherit = "delivery.grid"
    _name = "delivery.grid"
    _description = "Delivery Grid"

    def get_price_from_picking(self, cr, uid, id, total, weight, volume, quantity, context=None):
        grid = self.browse(cr, uid, id, context=context)
        price = 0.0
        ok = False
        price_dict = {'price': total, 'volume':volume, 'weight': weight, 'wv':volume*weight, 'quantity': quantity}
        for line in grid.line_ids:
            test = eval(line.type+line.operator+str(line.max_value), price_dict)
            if test:
                if line.price_type=='variable':
                    price = line.list_price * price_dict[line.variable_factor]
                else:
                    price = line.list_price
                ok = True
                break
        if not ok:
            raise osv.except_osv(_("Unable to fetch delivery method!"), _("Selected product in the delivery method doesn't fulfill any of the delivery grid(s) criteria."))
       
        percentage = grid.carrier_id.percentage
        price = (total * percentage)/ 100
        return price