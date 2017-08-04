# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import decimal_precision as dp
from osv import fields, osv


class product_template(osv.osv):
    _inherit = "product.template"
    _name = "product.template"

    _columns = {
        'standard_price': fields.float(
            'Cost Price',
            required=True,
            digits_compute=dp.get_precision('Standard Cost'),
            help="Product's cost for accounting stock valuation. " +
            "It is the base price for the supplier price."),
    }
