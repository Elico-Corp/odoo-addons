#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import netsvc
from osv import fields, osv
from mx import DateTime
from tools import config
from tools.translate import _

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def check_limit(self, cr, uid, ids, context={}):
		sp = self.browse(cr, uid, ids[0], context)
		so_obj= self.pool.get('sale.order')
		so = so_obj.browse(cr, uid, sp.sale_id ,context)
		partner = so.partner_id
        
		moveline_obj = self.pool.get('account.move.line')
		movelines = moveline_obj.search(cr, uid, [('partner_id', '=', partner.id),('account_id.type', 'in', ['receivable', 'payable']), ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
		movelines = moveline_obj.browse(cr, uid, movelines)

		debit, credit = 0.0, 0.0
		for line in movelines:
			if line.date_maturity < time.strftime('%Y-%m-%d'):
				credit += line.debit
				debit += line.credit

		if (credit - debit + so.amount_total) > partner.credit_limit:
			if not partner.over_credit:
				msg = 'Can not confirm picking move, Total mature due Amount %s as on %s !\nCheck Partner Accounts or Credit Limits !' % (credit - debit, time.strftime('%Y-%m-%d'))
				raise osv.except_osv(_('Credit Over Limits !'), _(msg))
				return False
			else:
				self.pool.get('res.partner').write(cr, uid, [partner.id], {'credit_limit':credit - debit + so.amount_total})
				return True
		else:
			return True
stock_picking()
