# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>, LIN Yu <lin.yu@elico-corp.com>
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

from openerp.tools import ustr
from openerp.osv import osv, fields
from openerp.tools.translate import _


#Add 2 extra prices in product + modify Retail price string in Restaurant price
class product_template(osv.osv):
    _inherit = 'product.template'
    _name    = 'product.template'
    
    def _get_price_current(self, cr, uid, ids, field_name, arg=None, context=None):
        user           = self.pool.get('res.users').browse(cr, 1, uid)
        price_type_obj = self.pool.get('product.price.type')
        price_type_ids = price_type_obj.search(cr, uid, [('field','=',arg['field_name']),'|',('company_id','=',user.company_id.id),('company_id','=',False)], order='company_id DESC')
        
        currency_name  = 'Unknown'
        if price_type_ids:
            price_type_id = price_type_ids[-1]
            currency_name = price_type_obj.browse(cr, uid, price_type_id).currency_id.name
        
        res = {}
        for id in ids:
            res[id] = currency_name
        return  res
    
    
    _columns = {
        'list_price':        fields.property(None, type='float', view_load=True, method=True, string='Sale Price 1'),
        'list2_price':       fields.property(None, type='float', view_load=True, method=True, string='Sale Price 2', help='HKD price'),
        'list3_price':       fields.property(None, type='float', view_load=True, method=True, string='Sale Price 3', help='CNY price'),
        
        'list_price_label':  fields.function(_get_price_current, type='char', size=4, arg={'field_name':'list_price'},),
        'list2_price_label': fields.function(_get_price_current, type='char', size=4, arg={'field_name':'list2_price'}),
        'list3_price_label': fields.function(_get_price_current, type='char', size=4, arg={'field_name':'list3_price'}),
    }

product_template()



class price_type(osv.osv):
    _inherit = 'product.price.type'
    _name    = 'product.price.type'
    
    def _check_field_company(self, cr, uid, ids, context=None):
        for pp in self.browse(cr, uid, ids):
            if not pp.company_id:
                if self.search(cr,uid,[('field','=',pp.field),('company_id','=',False),('id','!=',pp.id)]):
                    return False
        return True
    
    
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }
    
    #Dami: sql constraint does not work when field company_id is blank. Need to fix
    _sql_constraints=[
        ('field_company_uniq', 'unique(field,company_id)','Field and Company cannot be repeated' ),
    ]
    
#    _constraints=[
#       (_check_field_company, 'Error: Field and Company cannot be repeated', ['field','company_id'])
#    ]

price_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: