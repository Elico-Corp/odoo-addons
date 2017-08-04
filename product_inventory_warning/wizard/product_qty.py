# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import fields, osv
from tools.translate import _

class product_qty(osv.osv_memory):
    _name = "run.product.inventory"
    _description = "Compute Product Inventory"
    _columns = {

    }

    def compute_inventory(self, cr, uid, ids, context=None):
        """ To compute inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        pi_obj = self.pool.get('product.inventory')
        pi_obj.compute_inventory(cr, uid)

        mod_obj = self.pool.get('ir.model.data')

        res = mod_obj.get_object_reference(cr, uid, 'product_inventory_warning', 'view_product_inventory_tree')
        res_id = res and res[1] or False,

        return {
            'name': _('Product Inventory'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': res_id,
            'res_model': 'product.inventory',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': False,
        }
        #return {'type': 'ir.actions.act_window_close'}

product_qty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
