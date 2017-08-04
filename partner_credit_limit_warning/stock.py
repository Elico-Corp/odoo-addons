# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

import time
from osv import fields, osv
from tools.translate import _

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'validated': fields.boolean('Delivery',states={'done': [('readonly', True)]} ),
        'validator': fields.many2one('res.users', 'Validated by', states={'done': [('readonly', True)]}),
        
    }
    _defaults = {
        'validated': False
    }

    def on_change_validate(self, cr, uid, ids, validated=False):
        result = {
            'validated': validated,
            'validator': False, 
        }
        if not validated:
            return {'value': result}
        result = {
            'validated': validated,
            'validator': uid, 
        }
        return {'value': result}


    def check_limit(self, cr, uid, ids, context=None):
        if context is None:
            context = {'lang':self.pool.get('res.users').browse(cr, uid, uid, context=context).lang}
        sp = self.browse(cr, uid, ids[0], context)
        if not sp.sale_id or sp.type == 'internal' or sp.type == 'in':
            return True
        so_obj= self.pool.get('sale.order')
        so = so_obj.browse(cr, uid, sp.sale_id.id ,context)
        partner = so.partner_id
        
        moveline_obj = self.pool.get('account.move.line')
        movelines = moveline_obj.search(cr, uid, [('partner_id', '=', partner.id),('account_id.type', 'in', ['receivable', 'payable']), ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)

        debit, credit = 0.0, 0.0
        for line in movelines:
            if line.date_maturity < time.strftime('%Y-%m-%d'):
                credit += line.debit
                debit += line.credit

        partner_credit_limit = 0.0
        if not partner.is_company and partner.parent_id:
            partner_credit_limit = partner.parent_id.credit_limit
        else:
            partner_credit_limit = partner.credit_limit

        if (credit - debit + so.amount_total) > partner_credit_limit:
            if not sp.validated:
                msg = _('Can not confirm picking move, Total mature due Amount %s as on %s !\nCheck Partner Accounts or Credit Limits !') % (credit - debit + so.amount_total, time.strftime('%Y-%m-%d'))
                raise osv.except_osv(_('Credit Over Limits !'), msg)
                return False
            else:
                return True
        else:
            return True
stock_picking()
