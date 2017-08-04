# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class product_product(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'categ1_id': fields.many2one('product.category', 'Stat. Category 1',
                                     required=True),
        'categ2_id': fields.many2one('product.category', 'Stat. Category 2',
                                     required=True)
    }
