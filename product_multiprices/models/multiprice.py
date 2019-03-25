# -*- coding: utf-8 -*-
from openerp import fields, models
import openerp.addons.decimal_precision as dp


class Product(models.Model):

    _inherit = "product.template"

    list_price2 = fields.Float(
        'Sale Price 2', digits_compute=dp.get_precision('Product Price'))
    lst_price2 = fields.Float(
        related='list_price2', string='Sale Price 2',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price3 = fields.Float(
        'Sale Price 3', digits_compute=dp.get_precision('Product Price'))
    lst_price3 = fields.Float(
        related='list_price3', string='Sale Price 3',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price4 = fields.Float(
        'Sale Price 4', digits_compute=dp.get_precision('Product Price'))
    lst_price4 = fields.Float(
        related='list_price4', string='Sale Price 4',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price5 = fields.Float(
        'Sale Price 5', digits_compute=dp.get_precision('Product Price'))
    lst_price5 = fields.Float(
        related='list_price5', string='Sale Price 5',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price6 = fields.Float(
        'Sale Price 6', digits_compute=dp.get_precision('Product Price'))
    lst_price6 = fields.Float(
        related='list_price6', string='Sale Price 6',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price7 = fields.Float(
        'Sale Price 7', digits_compute=dp.get_precision('Product Price'))
    lst_price7 = fields.Float(
        related='list_price7', string='Sale Price 7',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price8 = fields.Float(
        'Sale Price 8', digits_compute=dp.get_precision('Product Price'))
    lst_price8 = fields.Float(
        related='list_price8', string='Sale Price 8',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price9 = fields.Float(
        'Sale Price 9', digits_compute=dp.get_precision('Product Price'))
    lst_price9 = fields.Float(
        related='list_price9', string='Sale Price 9',
        digits_compute=dp.get_precision('Product Price')
    )
    list_price10 = fields.Float(
        'Sale Price 10', digits_compute=dp.get_precision('Product Price'))
    lst_price10 = fields.Float(
        related='list_price10', string='Sale Price 10',
        digits_compute=dp.get_precision('Product Price')
    )
