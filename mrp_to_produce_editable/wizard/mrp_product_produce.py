# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class mrp_product_produce(orm.TransientModel):
    _name = "mrp.product.produce"
    _inherit = "mrp.product.produce"

    _columns = {
        'product_qty': fields.float(
            'Select Quantity',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True),
    }

    def _get_product_qty(self, cr, uid, context=None):
        """ To obtain product quantity
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return: Quantity
        <<<< rewrite this method to get the right number of product_qty
            to produce.
        """
        if context is None:
            context = {}
        prod = self.pool.get('mrp.production').browse(
            cr, uid,
            context['active_id'], context=context)
        unproduced_qty = 0
        for unproduced_product in prod.move_created_ids:
            if (unproduced_product.scrapped) or \
                    unproduced_product.state in (
                        'cancel', 'assigned', 'done') or\
                    (unproduced_product.product_id.id != prod.product_id.id):
                continue
            unproduced_qty += unproduced_product.product_qty
        return unproduced_qty or 0

    _defaults = {
        'product_qty': _get_product_qty,
    }

    def do_produce(self, cr, uid, ids, context=None):
        production_id = context.get('active_id', False)
        assert production_id, "Production Id should be specified in"
        " context as a Active ID."
        reasonable_qty = self._get_product_qty(cr, uid, context=context)
        data = self.browse(cr, uid, ids[0], context=context)
        if data.product_qty > reasonable_qty:
            raise osv.except_osv(
                _('Warning!'),
                _('You are going to produce total %s\n' +
                    'But you can only produce up to total %s quantities.') %
                (data.product_qty, reasonable_qty))
        self.pool.get('mrp.production').action_produce(
            cr, uid, production_id,
            data.product_qty, data.mode, context=context)
        return {}
