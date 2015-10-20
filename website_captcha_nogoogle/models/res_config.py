# -*- coding: utf-8 -*-
from openerp import fields, models


class website_config_settings(models.TransientModel):
    _inherit = 'website.config.settings'

    captcha_crypt_password = fields.Char(
        related='website_id.captcha_crypt_password')
    captcha_length = fields.Selection(
        related='website_id.captcha_length')
    captcha_chars = fields.Selection(
        related='website_id.captcha_chars')
