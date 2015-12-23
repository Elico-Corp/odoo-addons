# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class check_product_qty_report(models.Model):
    _name = "check.product.qty.report"
    _descript = "Check Product Qty Report"

    product_name = fields.Char(string='Product')
    product_qty = fields.Float(string='Number of material')
    stock_qty = fields.Float(string='Number of stock')
    can_product_qty = fields.Float(string='Number can be produced')
    diff_qty = fields.Float(string='Number of differences')
