# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import werkzeug

from openerp import http
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.auth_signup.res_users import SignupError
from openerp.http import request
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class AuthSignupInherit(AuthSignupHome):
    password_error_message = "Passwords do not match; please retype them."
    login_name_error_message = "Login name is duplicated. Please try another."

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                return super(AuthSignupHome, self).web_login(*args, **kw)
            except (SignupError, AssertionError), e:
                if e.message == self.password_error_message:
                    qcontext['error'] = _(u'两次填写的密码不一致，请重新填写密码')
                else:
                    qcontext['error'] = _(u'该用户名已经被注册，请重新填写用户名')

        return request.render('auth_signup.signup', qcontext)

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = dict((key, qcontext.get(key)) for key in (
            'login', 'name', 'password'))
        assert any([k for k in values.values()]), "The form was not properly \
        filled in."
        assert values.get('password') == qcontext.get(
            'confirm_password'), self.password_error_message
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()
