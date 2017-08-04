# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from osv import fields, osv
import netsvc

from tools.translate import _

# Overloaded sale_order to manage customer credit limit process :
class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def action_wait_before(self, cr, uid, ids, context=None):
        
        mod_obj =self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'partner_credit_limit_warning', 'view_sale_confirm_warning')
        res_id = res and res[1] or False
        for so in self.browse(cr, uid, ids, context=None):            
            if (so.partner_id.credit_limit > 0.0) and (so.partner_id.credit - so.partner_id.debit + so.amount_total) > so.partner_id.credit_limit:
                context['sale_id'] = so.id
                context['sale_name'] = so.name                            
                context['credit'] = so.partner_id.credit
                context['debit'] = so.partner_id.debit
                context['amount_total'] = so.amount_total
                context['credit_limit'] = so.partner_id.credit_limit
                            
                return {
                        'name':_('Warning'),
                        'view_mode': 'form',
                        'view_type': 'form',
                        'view_id': [res_id],
                        'res_model': 'sale.confirm.warning',
                        'context': context,
                        'type': 'ir.actions.act_window',
                        'nodestroy':True,
                        'target': 'new',
                }
            else:
                return self.pre_action_wait(cr, uid , [so.id,])


sale_order()
