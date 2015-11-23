# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Xiaopeng Xie
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
from openerp import models, fields


class check_product_qty_report(models.Model):
    _name = "check.product.qty.report"
    _descript = "Check Product Qty Report"

    product_name = fields.Char(string='产品')
    product_qty = fields.Float(string='需原料数')
    stock_qty = fields.Float(string='库存数')
    can_product_qty = fields.Float(string='可生产数')
    diff_qty = fields.Float(string='差异数')
