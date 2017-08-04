# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)



import time
from openerp.tools.translate import _
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'sample': fields.boolean('Is Sample? '),                
    }
    _defaults = {
        'delay': lambda *a: 1,
    }
    #move this button to modeul "sale_botton_price"
    #if not need button price 
    def product_uom_change(self, cursor, user, ids, sample, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):

        return True
        return self.product_id_change(cr, uid, ids, sample, pricelist, product,
                qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, update_tax=update_tax,
                date_order=date_order, context=context)

    # ref issue :Release 0911 SO blocked if product has package default selected 
    # by chen rong at 20140918
    def product_packaging_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False,
                                   partner_id=False, packaging=False, flag=False, context=None):

        res = super(sale_order_line, self).product_packaging_change(cr, uid, ids, pricelist, product, qty=qty, uom=uom,
                                   partner_id=partner_id, packaging=packaging, flag=False, context=context)

        res['warning'] = ''
        return res
    
sale_order_line()


class product_template(osv.osv):

    _inherit = 'product.template'
    _defaults = {
        'sale_delay': lambda *a: 1,
    }
