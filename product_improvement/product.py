# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Siyuan Gu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models


class product_product(models.Model):
    _inherit = 'product.product'

    # remove the constraint checking on EAN13
    def _check_ean_key(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_check_ean_key, '', ['ean13'])]

    _sql_constraints = [
        # make ean13 unique in system
        ('unique_ean13', 'unique (ean13)',
            "The EAN13 Barcode must be unique !"),
        # make internal reference unique in system
        ('unique_code', 'unique (default_code)',
            "The Internal Reference must be unique !"),
    ]
