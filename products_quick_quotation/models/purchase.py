from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create_quick_quotation(self,products,customer,model):
        lines = []
        if not products or not customer:
            return
        
        for product in products:
            val= {
                'product_id': product['product_id'],
                'product_uom_qty': product['product_qty'],
                'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            }
            lines.append((0,0,val))
        vals = {
            'partner_id': customer,
            'user_id': self.env.uid,
            'order_line': lines,
        }
        purchase_order = self.env['purchase.order'].sudo().create(vals)
        return purchase_order.id