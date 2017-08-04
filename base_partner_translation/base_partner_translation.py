# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


from osv import fields, orm


class res_company(orm.Model):
    _description = 'Companies'
    _inherit = "res.company"
    _name = "res.company"
    _columns = {
        'name': fields.char(
            'Company Name', size=64, required=True, translate=True),
    }


class res_partner(orm.Model):
    _description = 'Partner'
    _name = "res.partner"
    _inherit = "res.partner"
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True,
                            translate=True),
    }

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
