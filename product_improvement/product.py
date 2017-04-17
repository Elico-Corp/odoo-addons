# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class product_product(models.Model):
    _inherit = 'product.product'

    def _check_ean_key(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_check_ean_key, '', ['ean13'])]

    _sql_constraints = [
        ('unique_ean13', 'unique (ean13)',
            "The EAN13 Barcode must be unique !"),
        ('unique_code', 'unique (default_code)',
            "The Internal Reference must be unique !"),
    ]
