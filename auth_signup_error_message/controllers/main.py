# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Siyuan Gu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import werkzeug

from openerp.addons.auth_signup.res_users import SignupError
from openerp.http import request
from openerp import http
from openerp.tools.translate import _
from openerp.addons.auth_signup.controllers.main import AuthSignupHome

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
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get(
            'confirm_password'), self.password_error_message
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()
