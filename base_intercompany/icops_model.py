# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import logging
from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)


class icops_backend(orm.Model):
    _name = 'icops.backend'
    _description = 'ICOPS Backend'
    _inherit = 'connector.backend'

    _backend_type = 'icops'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('7.0', '7.0')]

    _columns = {
        'version': fields.selection(
            _select_versions,
            string='Version',
            required=True),
        'company_id': fields.many2one(
            'res.company', string="Company", required=True),
        'icops_ids': fields.one2many(
            'res.intercompany', 'backend_id', 'Inter-Company Setup'),
        'icops_uid': fields.many2one(
            'res.users', 'IC User',
            required=True,
            domain="[('company_id', '=', company_id)]",
            help="User to create update unlink IC records"),
        'model': fields.related(
            'backend_to', 'icops_uid', type='many2one',
            relation='res.users', readonly=True, string='IC User'),
    }

    _defaults = {
        'version': '7.0',
    }

    def _icops_backend(self, cr, uid, callback, domain=None,
                       context=None):
        if domain is None:
            domain = []
            ids = self.search(cr, uid, domain, context=context)
            if ids:
                callback(cr, uid, ids, context=context)

    def prepare_binding(self, cr, uid, data, context=None):
        context = context or {}
        icops_bind_ids = []
        if not 'icops_bind_ids' in data:
            data['icops_bind_ids'] = None
        if not 'icops' in context and not data['icops_bind_ids']:
            user = self.pool.get('res.users').browse(
                cr, uid, uid, context)
            backend_pool = self.pool.get('icops.backend')
            backend_ids = backend_pool.search(
                cr, uid, [('company_id', '=', user.company_id.id)])
            if backend_ids:
                backends = backend_pool.browse(
                    cr, uid, backend_ids, context)
                for backend in backends:
                    icops_bind_ids.append(
                        (0, 0, {'backend_id': backend.id}))
        return icops_bind_ids
