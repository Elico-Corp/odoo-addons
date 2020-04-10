# © 2020 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class CompanyFiling(models.Model):
    _inherit = 'website'

    certificate_number1 = fields.Char(string='Certificate Number1')
    certificate_number1_url = fields.Char(string='Certificate Number1 URL')
    certificate_url1 = fields.Char(string='Certificate URL1')
    certificate_logo1 = fields.Binary(string='Certificate Logo1')
    certificate_number2 = fields.Char(string='Certificate Number2')
    certificate_number2_url = fields.Char(string='Certificate Number2 URL')
    certificate_url2 = fields.Char(string='Certificate URL2')
    certificate_logo2 = fields.Binary(string='Certificate Logo2')


class CompanyFilingSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    certificate_number1 = fields.Char(
        string='Certificate Number1',
        related='website_id.certificate_number1',
        readonly=False,
    )
    certificate_number1_url = fields.Char(
        string='Certificate Number1 URL',
        related='website_id.certificate_number1_url',
        readonly=False,
    )
    certificate_url1 = fields.Char(
        string='Certificate URL1',
        related='website_id.certificate_url1',
        readonly=False,
    )
    certificate_logo1 = fields.Binary(
        string='Certificate Logo1',
        related='website_id.certificate_logo1',
        readonly=False,
    )
    certificate_number2 = fields.Char(
        string='Certificate Number2',
        related='website_id.certificate_number2',
        readonly=False,
    )
    certificate_number2_url = fields.Char(
        string='Certificate Number2 URL',
        related='website_id.certificate_number2_url',
        readonly=False,
    )
    certificate_url2 = fields.Char(
        string='Certificate URL2',
        related='website_id.certificate_url2',
        readonly=False,
    )
    certificate_logo2 = fields.Binary(
        string='Certificate Logo2',
        related='website_id.certificate_logo2',
        readonly=False,
    )
