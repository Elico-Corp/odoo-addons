# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv, fields
from tools.translate import _


class mrp_mo_split(osv.osv_memory):
    _name = 'mro.mo.split'

    _columns = {
        'quantity': fields.float('Quantity', required=True)
    }

    def split(self, cr, uid, ids, context=None):
        context = context or {}
        assert 'active_ids' in context
        active_id = context['active_id']
        productions = []
        for mro_mo_split in self.browse(
                cr, uid, ids, context=context):
            quantity = mro_mo_split.quantity
            if not quantity or quantity <= 0:
                raise osv.except_osv(_('Error !'), _(
                    'You must specify a value greater than 0.'))
            productions = self.pool.get('mrp.production')._split(
                cr, uid, active_id, quantity, context)
        return {
            'domain': "[('id','in',%s)]" % productions,
            'name': _('Production Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

