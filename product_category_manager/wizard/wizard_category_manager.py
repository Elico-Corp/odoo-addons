# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv, fields
from openerp.tools.translate import _


class wizard_category_manager(osv.osv_memory):
    _name = "wizard.category.manager"
    _columns = {
        'categ_from': fields.many2one(
            'product.category', 'Category Origin'),
        'categ_to': fields.many2one(
            'product.category', 'Category Destination')
    }

    def assign(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        wizard = self.browse(cr, uid, ids[0], context=context)
        categ_ids = []
        if wizard.categ_from:
            categ_ids.append((3, wizard.categ_from.id))
        if wizard.categ_to:
            categ_ids.append((4, wizard.categ_to.id))
        if not categ_ids:
            raise osv.except_osv(
                _('Warning!'),
                _('Please select at least one category'))
        product_pool = self.pool.get('product.product')
        product_pool.write(
            cr, uid, context['active_ids'],
            {'categ_ids': categ_ids})

    def remove_all(self, cr, uid, ids, context=None):
        product_pool = self.pool.get('product.product')
        product_pool.write(
            cr, uid, context['active_ids'], {'categ_ids': [(5,)]})
