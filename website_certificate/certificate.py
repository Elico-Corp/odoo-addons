# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class CompanyFiling(models.Model):
    _inherit = 'website'

    certificate_number1 = fields.Char(string='Certificate Number1')
    certificate_number1_url = fields.Char(string='Certificate Number1 URL')
    certificate_url1 = fields.Char(string='Certificate URL1')
    certificate_logo1 = fields.Binary(string='Certificate Logo1')
    certificate_number2 = fields.Char(string='Certificate Number2')
    certificate_url2 = fields.Char(string='Certificate URL2')
    certificate_logo2 = fields.Binary(string='Certificate Logo2')


class CompanyFilingSetting(models.TransientModel):
    _inherit = 'website.config.settings'

    certificate_number1 = fields.Char(
        string='Certificate Number1', related='website_id.certificate_number1')
    certificate_number1_url = fields.Char(
        string='Certificate Number1 URL',
        related='website_id.certificate_number1_url')
    certificate_url1 = fields.Char(
        string='Certificate URL1', related='website_id.certificate_url1')
    certificate_logo1 = fields.Binary(
        string='Certificate Logo1', related='website_id.certificate_logo1')
    certificate_number2 = fields.Char(
        string='Certificate Number2', related='website_id.certificate_number2')
    certificate_url2 = fields.Char(
        string='Certificate URL2', related='website_id.certificate_url2')
    certificate_logo2 = fields.Binary(
        string='Certificate Logo2', related='website_id.certificate_logo2')
