# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Qiao Lei <Qiao.lei@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distrisbuted in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
import re
from openerp.tools.translate import _


class product_pricecategory(osv.osv):

    _name = "product.pricecategory"
    _description = "Product Price Category"
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of product categories.")
    }

    _order = "sequence"

product_pricecategory()


class product_template(osv.osv):
    _inherit = 'product.template'
    
    _columns = {
        'pricecategory_id': fields.many2one('product.pricecategory','pricecategory_id', change_default=True,help="Select pricecategory for the current product"),
    }


class product_pricelist_item(osv.osv):
     _name = "product.pricelist.item"
     _inherit = 'product.pricelist.item'
     
     _columns = {
         'price_discount': fields.float('Price Discount', digits=(16,10)),
    }
product_pricelist_item()

