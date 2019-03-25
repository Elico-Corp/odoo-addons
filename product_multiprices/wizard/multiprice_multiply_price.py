# -*- coding: utf-8 -*-

from openerp import api, fields, models


class MultipriceMultiplyPrice(models.TransientModel):
    _name = "multiprice.multiply.price"
    _description = "Multiply selected sale price"

    column = fields.Selection(
        [
            ('list_price', 'Sale Price'),
            ('list_price2', 'Sale Price 2'),
            ('list_price3', 'Sale Price 3'),
            ('list_price4', 'Sale Price 4'),
            ('list_price5', 'Sale Price 5'),
            ('list_price6', 'Sale Price 6'),
            ('list_price7', 'Sale Price 7'),
            ('list_price8', 'Sale Price 8'),
            ('list_price9', 'Sale Price 9'),
            ('list_price10', 'Sale Price 10'),
        ], 'Column to multiply: ', required=True)
    by_value = fields.Float(
        'Multiply value', digit_compute=(6, 3), required=True)

    @api.one
    def action_multiply_price(self):
        product_ids = self.env['product.template'].browse(
            self._context['active_ids'])

        for product in product_ids:
            product[self.column] = product[self.column] * self.by_value
