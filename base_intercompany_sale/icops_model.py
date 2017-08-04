# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, orm


class icops_backend(orm.Model):
    _inherit = 'icops.backend'

    _columns = {
        'icops_shop_id': fields.many2one(
            'sale.shop', 'IC Default location',
            required=True),
    }
