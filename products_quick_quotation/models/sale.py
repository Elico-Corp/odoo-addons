from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create_quick_quotation(self,products,customer,model):
        lines = []
        if not products or not customer:
            return
        
        for product in products:
            val= {
                'product_id': product['product_id'],
                'product_uom_qty': product['product_qty'],
            }
            lines.append((0,0,val))
        vals = {
            'partner_id': customer,
            'user_id': self.env.uid,
            'order_line': lines,
        }
        sale_order = self.env['sale.order'].sudo().create(vals)
        return sale_order.id