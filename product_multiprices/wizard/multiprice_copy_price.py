# -*- coding: utf-8 -*-
from openerp import _, api, fields, models
from openerp.exceptions import Warning


class MultipriceCopyPrice(models.TransientModel):
    _name = "multiprice.copy.price"
    _description = "Copy one sale price to another"

    copy_from = fields.Selection(
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
        ], 'Copy from column: ', required=True)
    copy_to = fields.Selection(
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
        ], 'Copy to column: ', required=True)

    @api.one
    def action_copy_price(self):
        product_ids = self.env['product.template'].browse(
            self._context['active_ids'])

        if self.copy_from == self.copy_to:
            raise Warning(
                _(
                    """Please select two different price columns!"""
                )
            )

        for product in product_ids:
            product[self.copy_to] = product[self.copy_from]
