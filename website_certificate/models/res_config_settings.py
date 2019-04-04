# © 2015-2019 Elico corp (www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    certificate_number1 = fields.Char(
        string='Certificate Number1',
        related='website_id.certificate_number1',
        readonly=False)
    certificate_number1_url = fields.Char(
        string='Certificate Number1 URL',
        related='website_id.certificate_number1_url',
        readonly=False)
    certificate_url1 = fields.Char(
        string='Certificate URL1',
        related='website_id.certificate_url1',
        readonly=False)
    certificate_logo1 = fields.Binary(
        string='Certificate Logo1',
        related='website_id.certificate_logo1',
        readonly=False)
    certificate_number2 = fields.Char(
        string='Certificate Number2',
        related='website_id.certificate_number2',
        readonly=False)
    certificate_url2 = fields.Char(
        string='Certificate URL2',
        related='website_id.certificate_url2',
        readonly=False)
    certificate_logo2 = fields.Binary(
        string='Certificate Logo2',
        related='website_id.certificate_logo2',
        readonly=False)
