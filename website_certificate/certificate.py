# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CompanyFiling(models.Model):
    _inherit = 'website'

    certificate_url = fields.Char(string='ICP Certificate URL')
    logo = fields.Binary(string='ICP Certificate Logo')
    certificate_number = fields.Char(string='ICP Certificate Number')


class CompanyFilingSetting(models.TransientModel):
    _inherit = 'website.config.settings'

    certificate_url = fields.Char(string='ICP Certificate URL',
                                  related='website_id.certificate_url')
    logo = fields.Binary(string='ICP Certificate Logo',
                         related='website_id.logo')
    certificate_number = fields.Char(string='ICP Certificate Number',
                                     related='website_id.certificate_number')
