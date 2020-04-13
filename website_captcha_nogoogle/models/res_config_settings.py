# © 2015-2019 Elico corp (www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    captcha_crypt_password = fields.Char(
        related='website_id.captcha_crypt_password',
        readonly=False)
    captcha_length = fields.Selection(
        related='website_id.captcha_length',
        readonly=False)
    captcha_chars = fields.Selection(
        related='website_id.captcha_chars',
        readonly=False)
