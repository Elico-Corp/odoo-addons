# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import fields, osv
from tools.translate import _

class stock_slowing_move(osv.osv_memory):
    _name = "stock.slowing.move"
    _description = "Compute Slowing Move"
    _columns = {

    }

    def compute_slowingmove(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        slow_obj = self.pool.get('stock.slowmove')
        slow_obj.process_slowmove(cr, uid)

        mod_obj = self.pool.get('ir.model.data')

        res = mod_obj.get_object_reference(cr, uid, 'stock_report_slowmoving', 'view_stock_slowmove_tree')
        res_id = res and res[1] or False,

        return {
            'name': _('Stock Slow Moving'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': res_id,
            'res_model': 'stock.slowmove',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': False,
        }

stock_slowing_move()

