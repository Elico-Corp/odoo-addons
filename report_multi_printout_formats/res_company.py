# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class res_company(orm.Model):
    _inherit = 'res.company'

    def _lang_get(self, cr, uid, context=None):
        lang_pool = self.pool.get('res.lang')
        ids = lang_pool.search(cr, uid, [], context=context)
        res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res]

    _columns = {
        'alt_language': fields.selection(
            _lang_get,
            'Alternative Language',
            help='Please input here the language you want to force in ' +
            'the printouts (SO, PO, SI, PI and stock picking)')
    }
