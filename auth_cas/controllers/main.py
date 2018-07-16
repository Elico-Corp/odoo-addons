# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import urllib
import odoo

from odoo.modules.registry import RegistryManager
from odoo.addons.web.controllers.main import login_and_redirect
from odoo import SUPERUSER_ID
from openid.cryptutil import randomString
from urlparse import urlparse

from ..pycas import login

from odoo import http
from odoo.addons.web.controllers import main
from odoo.http import request

import werkzeug
import logging
_logger = logging.getLogger(__name__)


class Controller(http.Controller):
    _cp_path = '/auth_cas'

    @staticmethod
    def get_config_static(req, dbname):
        """ Retrieves the module config for the CAS authentication. """
        # registry = RegistryManager.get(dbname)
        # with registry.cursor() as cr:
        #     print ">>>>>>>>>>>>>>>>",cr,request
        icp = request.env['ir.config_parameter'].sudo()
        config = {
            'login_cas': icp.get_param('cas_auth.cas_activated'),
            'host': icp.get_param('cas_auth.cas_server'),
            'port': icp.get_param('cas_auth.cas_server_port'),
            'auto_create': icp.get_param('cas_auth.cas_create_user'),
        }

        return config

    @http.route('/auth_cas/get_config', type='json')
    def get_config(self, req, dbname):
        """ Retrieves the module config for the CAS authentication. """
        # registry = RegistryManager.get(dbname)
        # with registry.cursor() as cr:
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
            query = urlparse.urlparse(url).query
            res = dict(
                [(k, v[0]) for k, v in urlparse.parse_qs(query).items()])
            res1 = {}
            if res.get('redirect', {}):
                res1 = qs(res.get('redirect', {}))
            res.update(res1)
            # todo if one ticket in redirect
            # and one ticket in normal path, deal ticket
            return res
        return qs(url).get('ticket', '')

    def _cas_login(self, redirect=None, **kw):
        cas_url, service_url, dbname = self._get_config_url()

        ticket = self._get_cas_ticket(request)
        if not ticket:
            cas_login = cas_url + '/login?service=' + service_url
            # response
            return werkzeug.utils.redirect(cas_login)
            # return http.redirect_with_hash(cas_redirect)
        else:
            # userName = self.validateCASTicket(ticket, cas_url, service_url)
            status, userName, cookie = login(cas_url, service_url, ticket)
            ids = []
            if userName and status == 0:
                # def getUidFromUserName(userName):
                registry = RegistryManager.get(dbname)
                cr = registry.cursor()
                users = registry.get('res.users')
                ids = users.search(
                    cr, SUPERUSER_ID, [('login', '=', userName)])
                assert len(ids) == 1
                cas_key = randomString(
                    16, '0123456789abcdefghijklmnopqrstuvwxyz')
                users.write(cr, SUPERUSER_ID, ids, {'cas_key': cas_key})
                # set cookie for relogin
                res = login_and_redirect(dbname, userName, cas_key)
                return res
        return

    @http.route('/web/login', type='json', auth="none")
    def web_login(self, redirect=None, **kw):

        config = Controller.get_config_static(request, request.session.db)
        if config.get('login_cas', False) == u'True':
            res = self._cas_login(redirect)
            if res:
                return res

        return "Failed"

    @http.route('/auth_cas/cas_authenticate', type='http')
    def cas_authenticate(
            self, req, dbname, cur_url, cas_host, cas_port,
            auto_create, ticket):
        """
        Checks if the user attempts to authenticate is authorized
        to do it and, if it is, authenticate him.
        """

        if cas_port == -1:
            cas_server = cas_host
        else:
            url_server = urlparse(cas_host)
            cas_server = url_server.scheme + '://' + url_server.netloc + ':' \
                + str(cas_port) + url_server.path
        service_url = urllib.quote(cur_url, safe='')
        # The login function, from pycas, check if the ticket given
        # by CAS is a real ticket. The login of the user
        # connected by CAS is returned.
        status, idUser, cookie = login(cas_server, service_url, ticket)
        result = False

        if idUser and status == 0:
            registry = RegistryManager.get(dbname)
            cr = registry.cursor()
            users = registry.get('res.users')
            ids = users.search(cr, SUPERUSER_ID, [('login', '=', idUser)])

            assert len(ids) < 2

            # We check if the user authenticated have an odoo account
            # or if the auto_create field is True
            if ids or auto_create == 'True':
                if ids:
                    user_id = ids[0]
                # If the user have no account, we create one
                else:
                    user_id = users.create(cr, SUPERUSER_ID, {
                        'name': idUser.capitalize(), 'login': idUser})

                # A random key is generated in order to verify if the
                # login request come from here or if the user
                # try to authenticate by any other way
                cas_key = randomString(
                    16, '0123456789abcdefghijklmnopqrstuvwxyz')

                users.write(cr, SUPERUSER_ID, [user_id], {'cas_key': cas_key})

                login_and_redirect(dbname, idUser, cas_key)

                result = {'status': status, 'session_id': req.session_id}
            else:
                result = {
                    'status': status, 'fail': True,
                    'session_id': req.session_id}

            cr.close()

        if not result:
            result = {'status': status}

        return result


class Home(main.Home):

    def _get_cas_ticket(self, request):
        # get ticket from url
        url = request.httprequest.url

        def qs(url):
            query = urlparse.urlparse(url).query
            res = dict([
                (k, v[0]) for k, v in urlparse.parse_qs(query).items()])
            res1 = {}
            if res.get('redirect', {}):
                res1 = qs(res.get('redirect', {}))
            res.update(res1)
            # todo if one ticket in redirect and one ticket
            # in normal path, deal ticket
            return res
        return qs(url).get('ticket', '')

    @staticmethod
    def _get_config_url():
        config = Controller.get_config_static(request, request.session.db)
        cas_url = config['host'] + ':' + config['port']
        service_url = request.httprequest.url_root
        dbname = request.session.db
        return cas_url, service_url, dbname

    def _cas_login(self, redirect=None, **kw):
        cas_url, service_url, dbname = self._get_config_url()

        ticket = self._get_cas_ticket(request)
        if not ticket:
            cas_login = cas_url + '/login?service=' + service_url
            # response
            return werkzeug.utils.redirect(cas_login)
            # return http.redirect_with_hash(cas_redirect)
        else:
            # userName = self.validateCASTicket(ticket, cas_url, service_url)
            status, userName, cookie = login(cas_url, service_url, ticket)
            ids = []
            if userName and status == 0:
                # def getUidFromUserName(userName):
                registry = RegistryManager.get(dbname)
                cr = registry.cursor()
                users = registry.get('res.users')
                ids = users.search(
                    cr, SUPERUSER_ID, [('login', '=', userName)])
                assert len(ids) == 1
                cas_key = randomString(
                    16, '0123456789abcdefghijklmnopqrstuvwxyz')
                users.write(cr, SUPERUSER_ID, ids, {'cas_key': cas_key})
                # set cookie for relogin
                res = login_and_redirect(dbname, userName, cas_key)
                return res
        return

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        main.ensure_db()
        config = Controller.get_config_static(request, request.session.db)
        if config.get('login_cas', False) == u'True':
            res = self._cas_login(redirect)
            if res:
                return res

        if request.httprequest.method == 'GET' and redirect and \
           request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        if not redirect:
            redirect = '/web?' + request.httprequest.query_string
        values['redirect'] = redirect

        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(
                request.session.db, request.params['login'],
                request.params['password'])
            if uid is not False:
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = "Wrong login/password"
        return request.render('web.login', values)


class Session(main.Session):

    def _cas_logout(self):
        _logger.debug("!! cas logout")
        # self.clear_cookie("UserName")
        casUrl, serviceUrl, dbName = Home._get_config_url()
        logout_url = casUrl + '/logout'
        return werkzeug.utils.redirect(logout_url)

    def cas_logout(self):
        return self._cas_logout()

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        config = Controller.get_config_static(request, request.session.db)
        if config.get('login_cas', False) == u'True':
            return self.cas_logout()
        else:
            return werkzeug.utils.redirect(redirect, 303)
