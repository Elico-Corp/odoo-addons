# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, osv


class  stock_tracking(osv.osv):
    _inherit ='stock.tracking'
    def _get_net_weight(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for pack in self.browse(cr, uid, ids, context=context):
            res[pack.id] = sum([m.product_id.weight_net * m.product_qty for m in pack.move_ids])
        return res
    
    _columns={
        'ul_id':    fields.many2one('product.ul','Pack Template'),
        'pack_h':   fields.related('ul_id', 'high', string='H (cm)', type='float', digits=(3,3), readonly=True),
        'pack_w':   fields.related('ul_id', 'width', string='W (cm)', type='float', digits=(3,3), readonly=True),
        'pack_l':   fields.related('ul_id', 'long', string='L (cm)', type='float', digits=(3,3), readonly=True),
        'pack_cbm': fields.related('ul_id', 'cbm', string='CBM',    type='float', digits=(3,3), readonly=True),

        'pack_address': fields.char('Address', size=128),
        'pack_note':    fields.char('Note', size=128),

        'gross_weight': fields.float('GW (Kg)'),
        'net_weight':   fields.function(_get_net_weight, arg=None, type='float', string='NW (Kg)'),
    }



