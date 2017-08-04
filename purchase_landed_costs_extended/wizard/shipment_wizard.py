# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields


class landed_costs_shipment_po(orm.TransientModel):

    _name = 'landed.costs.shipment.po'
    _columns = {
        'purchase_ids': fields.many2many(
            'purchase.order', 'landed_cost_shipment_group_rel',
            'shipment_id', 'po_id',
            'Purchase Order',
            domain=[('shipment_id', '=', False)]),
    }

    def link_po(self, cr, uid, ids, context=None):
        purchase_obj = self.pool.get('purchase.order')
        for assigner in self.browse(cr, uid, ids, context=context):
            po_ids = [po.id for po in assigner.purchase_ids]
            if context and context.get('active_id', False):
                # link the pos to the current shipment
                for po in purchase_obj.browse(cr, uid, po_ids, context=context):
                    po.write({'shipment_id': context.get('active_id')})
                    
        return {'type': 'ir.actions.act_window_close'}

    def confirm(self, cr, uid, ids, context=None):
        shipment_id = context.get('active_id', False)
