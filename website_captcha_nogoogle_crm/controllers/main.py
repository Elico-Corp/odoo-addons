# © 2015-2018 Elico corp (www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm


class WebsiteForm(WebsiteForm):

    @http.route('/website_form/<string:model_name>', type='http',
                auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        res = super(WebsiteForm, self).website_form(model_name, **kwargs)
        data = json.loads(res.data.decode('utf-8'))
        if model_name == 'crm.lead' and \
                not request.params.get('state_id') and \
                data is not False:
            crypt_challenge = kwargs.get('captcha_challenge_field', None)
            response = kwargs.get('captcha_response_field', None)
            if not crypt_challenge or not response:
                pass
            elif request.website.is_captcha_valid(crypt_challenge, response):
                return res
            data = {
                'error_fields': data['error_fields'] +
                                    ['captcha_response_field']
                if 'error_fields' in data else ['captcha_response_field']
            }
            res = json.dumps(data)
        return res
