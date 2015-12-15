# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.web.controllers.main import ensure_db


class WebInherit(AuthSignupHome):
    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(WebInherit, self).web_login(*args, **kw)
        response.qcontext.update({'redirect': '/shop'})

        return response
