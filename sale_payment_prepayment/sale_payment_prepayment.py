# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class payment_method(orm.Model):
    _inherit = "payment.method"
    _columns = {
        'is_prepayment': fields.boolean('Prepayment', help='Check this box if you want the payment method to create a prepayment payment using the prepayment account instead of direct accounting moves linked to receivable account'),
    }
    _defaults={       
    }
    
    
class sale_order(orm.Model):
    _inherit = 'sale.order'
    def _prepare_payment_move_line(self, cr, uid, move_name, sale, journal,
                                       period, amount, date, context=None):
        debit_line, credit_line = super(sale_order, self)._prepare_payment_move_line(cr, uid, move_name, sale, journal,
                                        period, amount, date, context=context)
        
        if sale.payment_method_id and sale.payment_method_id.is_prepayment:
            credit_line.update({'account_id': sale.partner_id.property_account_prereceivable.id,})
            
        return debit_line, credit_line
    
    
    
 
  
