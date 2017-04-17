# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    tracking_number = fields.Char(string="Tracking Number")
