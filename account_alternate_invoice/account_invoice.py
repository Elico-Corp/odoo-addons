# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

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


  