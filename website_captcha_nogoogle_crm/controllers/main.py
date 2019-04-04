# © 2015-2018 Elico corp (www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request
import odoo.addons.website_crm.controllers.main as main


class ContactUs(main.contactus):

    @http.route(['/crm/contactus'], type='http', auth="public",
                website=True, multilang=True)
    def contactus(self, *args, **kw):
        crypt_challenge = kw.pop('captcha_challenge_field', None)
        response = kw.pop('captcha_response_field', None)
        if not kw or not crypt_challenge or not response:
            pass
        elif request.website.is_captcha_valid(crypt_challenge, response):
            return super(ContactUs, self).contactus(*args, **kw)
        values = dict(kw, error=['captcha_response_field'], kwargs=kw.items())
        return request.website.render(
            kw.get("view_from", "website.contactus"), values)
