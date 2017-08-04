# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, osv


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'
    _name = 'stock.picking.out'

    def action_process(self, cr, uid, ids, context=None):
        '''inherit from stock/stock.py, check if this picking is paid.'''
        sale_obj = self.pool.get('sale.order')
        settings_obj = self.pool.get('stock.config.settings')
        for picking in self.browse(cr, uid, ids, context=context):
            #TODO: how about the DO that has no origin?
            if picking.origin:
                domain = [('name', '=', picking.origin)]
                sale_ids = sale_obj.search(cr, uid, domain, context=context)
                for sale in sale_obj.browse(cr, uid, sale_ids, context):
                    if not sale.invoiced:
                        raise osv.except_osv('Warning', 'The SO %s must be\
                              fully paid before you can process this delivery.' % picking.origin)
        return super(stock_picking_out, self).action_process(cr, uid, ids, context)
