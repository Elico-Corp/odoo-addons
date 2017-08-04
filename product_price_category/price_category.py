# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

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

