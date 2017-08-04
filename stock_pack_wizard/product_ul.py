# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import fields, osv


class product_ul(osv.osv):
    _inherit = 'product.ul'
    def _get_cbm(self, cr, uid, ids, fields, arg=None,  context=None):
        res = {}
        for ul in self.browse(cr, uid, ids, context=context):
            cbm = ul.high * ul.width * ul.long 
            cbm = cbm != 0 and cbm/1000000 
            res[ul.id] = cbm
            
        return res
    _columns = {
        'name': fields.char('name', size=32),
        'high': fields.float('H (cm)', digits=(3,3)),
        'width':fields.float('W (cm)', digits=(3,3)),
        'long': fields.float('L (cm)', digits=(3,3)),
        'cbm': fields.function(_get_cbm, arg=None, type='float', digits=(3,3), string='CBM'),
    }

 
