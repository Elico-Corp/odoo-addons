# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from openerp import tools
from tools.translate import _
import openerp.addons.decimal_precision as dp

class product_supplierinfo(osv.osv):
    _inherit = 'product.supplierinfo'
    
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
            supplier_info = self.browse(cr, uid, id)
            for f in field_names:
                if f == 'qty_available':
                    res[id][f] = supplier_info.product_id.qty_available
                if f == 'virtual_available':
                    res[id][f] = supplier_info.product_id.virtual_available
        return res
    
    _columns={
        'product_id' : fields.many2one('product.product', 'Product', select=1, ondelete='cascade', required=True),
        'qty_available' : fields.function(_product_available,multi='qty_available',type='float',digits_compute=dp.get_precision('Product Unit of Measure'),string="Quantity On Hand"),
        'virtual_available' : fields.function(_product_available,multi='qty_available',type='float', digits_compute=dp.get_precision('Product Unit of Measure'),string="Forecasted Quantity"),
    }
product_supplierinfo()


