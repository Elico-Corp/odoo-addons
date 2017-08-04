# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class product_product(orm.Model):
    _inherit = 'product.product'

    def _get_cubic_weight(self, cr, uid, ids, name, args, context=None):
        res = {}
        for product in self.browse(cr, uid, ids):
            res[product.id] = product.height / 100.0 * product.width / 100.0 * product.length / 100.0 * 250.0
        return res

    def onchange_hwl(self, cr, uid, ids, height, width, length, context=None):
        res = {}
        res['volume'] = height / 100.0 * width / 100.0 * length / 100.0
        return {'value': res}

    _columns = {'cubic_weight': fields.function(
                _get_cubic_weight,
                type='float', store=True, string='Cubic Weight (kg)'),
                'height': fields.float('Height (cm)'),
                'width': fields.float('Width (cm)'),
                'length': fields.float('Length (cm)'),
                }
