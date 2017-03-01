# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class WebSiteInherit(models.Model):
    _inherit = 'website'

    def check_stock_inventory(self, product_id, quantity):
        if product_id:
            product = self.env['product.template'].sudo().browse(product_id.id)

            if product and product.qty_available >= quantity:
                return True
            else:
                return False

        return True
