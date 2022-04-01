from odoo import api, fields, models

class View(models.Model):
    _inherit = 'ir.ui.view'
    
    type = fields.Selection(selection_add=[
        ('quickquotationview', 'Qucik Quotation View')
    ], ondelete={'quickquotationview': 'cascade'})