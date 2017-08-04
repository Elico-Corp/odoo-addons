# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import fields, orm


class product_product(orm.Model):
    _inherit = 'product.product'

    def write(self, cr, uid, ids, vals, context=None):
        user_pool = self.pool.get('res.users')
        # check if user belong to portal
        # if yes, the state of product will become draft
        is_portal = user_pool.has_group(cr, uid, 'portal.group_portal')
        if is_portal:
            vals.update({'state': 'draft'})

        return super(product_product, self).write(
            cr, uid, ids, vals, context=context)
