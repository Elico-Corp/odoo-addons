# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.web import http
from openerp.addons.web.http import request
import openerp.addons.website_crm.controllers.main as main


class contactus(main.contactus):

    @http.route(['/crm/contactus'], type='http', auth="public",
                website=True, multilang=True)
    def contactus(self, *args, **kw):
        crypt_challenge = kw.pop('captcha_challenge_field', None)
        response = kw.pop('captcha_response_field', None)
        if not kw or not crypt_challenge or not response:
            pass
        elif request.website.is_captcha_valid(crypt_challenge, response):
            return super(contactus, self).contactus(*args, **kw)
        values = dict(kw, error=['captcha_response_field'], kwargs=kw.items())
        return request.website.render(
            kw.get("view_from", "website.contactus"), values)
