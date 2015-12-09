# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class WebsiteConfigSettings(models.TransientModel):

    _inherit = "website.config.settings"

    website_slide_google_app_key = fields.Char(string='Google Doc Key')

    @api.model
    def get_website_slide_google_app_key(self, fields):
        website_slide_google_app_key = False
        if 'website_slide_google_app_key' in fields:
            website_slide_google_app_key = self.env['ir.config_parameter'].\
                sudo().get_param('website_slides.google_app_key')
        return {
            'website_slide_google_app_key': website_slide_google_app_key
        }

    @api.multi
    def set_website_slide_google_app_key(self):
        for wizard in self:
            self.env['ir.config_parameter'].sudo().set_param(
                'website_slides.google_app_key',
                wizard.website_slide_google_app_key)
