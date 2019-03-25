# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.osv import osv, fields


class ResPartner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'property_account_prepayable': fields.many2one(
            'account.account',
            string="Account Payable (Prepayment)",
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the \
                prepayment payable account for the current partner"),
        'property_account_prereceivable': fields.many2one(
            'account.account',
            string="Account Receivable (Prepayment)",
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the \
                prepayment receivable account for the current partner"),
    }


res_partner()
