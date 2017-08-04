# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv
from openerp.tools.translate import _


class landed_cost_position_invoice(osv.osv_memory):

    """ To create invoice for purchase order line"""

    _name = 'landed.cost.position.invoice'
    _description = 'Landed Cost Position Make Invoice'

    def make_invoices(self, cr, uid, ids, context=None):

        context = context or None
        record_ids = context.get('active_ids', [])
        invoice_ids = []
        if record_ids:
            lcp_pool = self.pool.get('landed.cost.position')
            po_pool = self.pool.get('purchase.order')

            for order_cost in lcp_pool.browse(cr, uid, record_ids,
                                              context=context):
                if order_cost.generate_invoice and not order_cost.invoice_id:
                    inv_id = po_pool._generate_invoice_from_landed_cost(
                        cr, uid, order_cost, context=context)
                    invoice_ids.append(inv_id)
        domain = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"
        return {
            'domain': domain,
            'name': _('Landed Cost Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
            'type': 'ir.actions.act_window'
        }
