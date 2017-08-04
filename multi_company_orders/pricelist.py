# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields


class product_pricelist(orm.Model):
    _inherit = 'product.pricelist'
    _columns = {
        'intercompany': fields.boolean('Intercompany')
    }
