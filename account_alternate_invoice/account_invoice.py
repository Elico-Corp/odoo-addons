# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#     Jon Chow <jon.chow@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'alternative_discount': fields.integer(
            'Alternative Discount',
            help='Discount to be applied to the alternative invoice'),
    }
    _defaults = {
        'alternative_discount':lambda *a: 0,    
    }
    _sql_constraints = [
        ('check_alternative_discount', 'CHECK (alternative_discount<100 AND alternative_discount>-1)', 'Alternative Discount must in 0-100'),
    ]

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
  