# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    captcha_crypt_password = fields.Char(
        related='website_id.captcha_crypt_password')
    captcha_length = fields.Selection(
        related='website_id.captcha_length')
    captcha_chars = fields.Selection(
        related='website_id.captcha_chars')
