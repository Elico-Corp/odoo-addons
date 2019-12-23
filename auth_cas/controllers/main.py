# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016-2018 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import urllib
from odoo.addons.web.controllers.main import login_and_redirect
from openid.cryptutil import randomString
from odoo.exceptions import AccessDenied
import urllib.parse

from ..pycas import login

from odoo import http
from odoo.addons.web.controllers import main
from odoo.http import request

import werkzeug
import logging

_logger = logging.getLogger(__name__)


class Controller(http.Controller):

    @staticmethod
    def get_config_static():
        """ Retrieves the module config for the CAS authentication. """
        icp = request.env['ir.config_parameter'].sudo()
        config = {
            'login_cas': icp.get_param('cas_auth.cas_activated'),
            'host': icp.get_param('cas_auth.cas_server'),
            'port': icp.get_param('cas_auth.cas_server_port'),
            'auto_create': icp.get_param('cas_auth.cas_create_user'),
        }

        return config

    def _get_cas_ticket(self, request):
        # get ticket from url
        url = request.httprequest.url

        def qs(url):
            query = urllib.parse.urlparse(url).query
            res = dict(
                [(k, v[0]) for k, v in urllib.parse.parse_qs(query).items()])
            res1 = {}
            if res.get('redirect', {}):
                res1 = qs(res.get('redirect', {}))
            res.update(res1)
            # TODO if one ticket in redirect
            # and one ticket in normal path, deal ticket
            return res

        return qs(url).get('ticket', '')

    @http.route('/auth_cas/cas_authenticate', type='http', auth="none")
    def cas_authenticate(self):
        config = Controller.get_config_static()
        service_url = request.httprequest.url_root
        cas_login = \
            config.get('host') + ':' + config.get('port') + \
            '/cas/login?service=' + service_url
        # response
        return werkzeug.utils.redirect(cas_login)

    @staticmethod
    def cas_authenticate_user(
            req, dbname, cur_url, cas_host, cas_port, auto_create, ticket):
        """
        Checks if the user attempts to authenticate is authorized
        to do it and, if it is, authenticate him.
        """
        if cas_port == -1:
            cas_server = cas_host
        else:
            url_server = urllib.parse.urlparse(cas_host)
            cas_server = \
                url_server.scheme + '://' + url_server.netloc + \
                ':' + str(cas_port) + url_server.path
        service_url = urllib.quote(cur_url, safe='')
        # The login function, from pycas, check if the ticket given
        # by CAS is a real ticket. The login of the user
        # connected by CAS is returned.
        status, idUser, cookie = login(cas_server, service_url, ticket)
        result = False
        if idUser and status == 0:
            users = request.env['res.users'].sudo()
            user_id = users.search([('login', '=', idUser)])
            assert len(user_id) < 2

            # We check if the user authenticated have an odoo account
            # or if the auto_create field is True
            if user_id or auto_create == 'True':
                if not user_id:
                    user_id = users.create({
                        'name': idUser.capitalize(), 'login': idUser})

                # A random key is generated in order to verify if the
                # login request come from here or if the user
                # try to authenticate by any other way
                cas_key = randomString(
                    16, '0123456789abcdefghijklmnopqrstuvwxyz')
                user_id.write({'cas_key': cas_key, 'password': cas_key})
                request.cr.commit()
                try:
                    login_and_redirect(dbname, idUser, cas_key)
                except AccessDenied:
                    values = {}
                    values['databases'] = http.db_list()
                    values['error'] = "Wrong login/password"
                    return request.render('web.login', values)
                result = {'status': status}
            else:
                result = {
                    'status': status, 'fail': True}

        if not result:
            result = {'status': status}

        return result


class Home(main.Home):

    @http.route()
    def index(self, s_action=None, db=None, **kw):
        ticket = self._get_cas_ticket(request)
        if ticket:
            config = Controller.get_config_static()

            cas_url, service_url, dbname = self._get_config_url()
            Controller.cas_authenticate_user(
                request, dbname, service_url, config.get('host'),
                config.get('port'), config.get('auto_create'), ticket)
        return super(Home, self).index(s_action, db, **kw)

    def _get_cas_ticket(self, request):
        # get ticket from url
        url = request.httprequest.url

        def qs(url):
            query = urllib.parse.urlparse(url).query
            res = dict([
                (k, v[0]) for k, v in urllib.parse.parse_qs(query).items()])
            res1 = {}
            if res.get('redirect', {}):
                res1 = qs(res.get('redirect', {}))
            res.update(res1)
            return res

        return qs(url).get('ticket', '')

    @staticmethod
    def _get_config_url():
        config = Controller.get_config_static()
        cas_url = config['host'] + ':' + config['port']
        service_url = request.httprequest.url_root
        dbname = request.session.db
        return cas_url, service_url, dbname


class Session(main.Session):

    def _cas_logout(self):
        _logger.debug("!! cas logout")
        casUrl, serviceUrl, dbName = Home._get_config_url()

        logout_url = casUrl + '/cas/logout?service=' + serviceUrl
        return werkzeug.utils.redirect(logout_url)

    def cas_logout(self):
        return self._cas_logout()

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        config = Controller.get_config_static()
        if config.get('login_cas', False) == u'True':
            return self.cas_logout()
        else:
            return werkzeug.utils.redirect(redirect, 303)
