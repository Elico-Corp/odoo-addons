# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp import netsvc
from openerp import pooler, tools
import math
from openerp.tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
import time
from openerp.osv import fields, osv



class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
                'pdt_pline': fields.one2many('product.pricelist.item', 'product_id', 'Product Pricelist Line', required=False,context={'product_id':'id'}),
    }
product_product()


class product_pricelist_item(osv.osv):
    _inherit='product.pricelist.item'
    
    def create(self,cr,uid,values,context=None):
        print values ,'#', context
        return super(product_pricelist_item,self).create(cr,uid,values,context=context)
    
    
product_pricelist_item()






