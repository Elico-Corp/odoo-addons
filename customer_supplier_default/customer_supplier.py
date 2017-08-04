# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm

class res_partner(orm.Model):
    _inherit = 'res.partner'
    #Un-select customer or supplier by default when creating contacts for companies.
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(res_partner, self).default_get(cr, uid, fields, context=context)
        if context.get('customer', False) == False:
            res['customer'] = False
        if context.get('supplier', False) == False:
            res['supplier'] = False
        return res

