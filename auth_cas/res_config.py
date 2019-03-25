# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
from urlparse import urlparse

_logger = logging.getLogger(__name__)

try:
    from auth_cas.pycas import login
except (ImportError, IOError) as err:
    _logger.debug(err)
default_host = 'https://localhost'
default_port = 8443


class CasBaseConfigSettings(osv.TransientModel):
    """
    The fields declared here are used to manage settings of the CAS server.
    """
    _inherit = 'base.config.settings'
    _columns = {
        'cas_activated': fields.boolean(
            'CAS authentication activated',
            help='The CAS authentication only works if you are in a single database mode. \
You can launch the Odoo Server with the option --db-filter=YOUR_DATABASE \
to do so.'),
        'cas_server': fields.char('CAS Server address', size=64),
        'cas_server_port': fields.integer('CAS Server port'),
        'cas_create_user': fields.boolean(
            'Users created on the fly',
            help='Automatically create local user accounts for new users authenticating \
via CAS'),
    }

    # Getter is required for fields stored in base.config.settings
    def get_default_cas_values(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        return {
            'cas_activated': safe_eval(icp.get_param(
                cr, uid, 'cas_auth.cas_activated', 'False')),
            'cas_server': icp.get_param(
                cr, uid, 'cas_auth.cas_server', default_host),
            'cas_server_port': int(icp.get_param(
                cr, uid, 'cas_auth.cas_server_port', default_port)),
            'cas_create_user': safe_eval(icp.get_param(
                cr, uid, 'cas_auth.cas_create_user', 'True')),
        }

    # Setter is required too
    def set_cas_values(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')

        error = True

        # If the host OR the port is valid
        if config.cas_server or config.cas_server_port:
            # If the host AND the port are valid,
            # we can activate CAS authentication and save all values
            if config.cas_server and config.cas_server_port:
                if config.cas_activated:
                    icp.set_param(
                        cr, uid, 'cas_auth.cas_activated',
                        str(config.cas_activated))
                    # There is no error
                    error = False
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server', config.cas_server)
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server_port',
                    config.cas_server_port)
            # Else, there is one error
            # If the host field is valid, we save it and the default port value
            elif config.cas_server:
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server', config.cas_server)
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server_port', default_port)
            # Else, the host field is empty,
            # but not the port field: we save it and the default host value
            else:
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server_port',
                    config.cas_server_port)
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server', default_host)
        # If error is True, there is at least one error,
        # so we deactivate CAS authentication
        if error:
            icp.set_param(cr, uid, 'cas_auth.cas_activated', 'False')
            # If the host field is empty, we save his default value
            if not config.cas_server:
                icp.set_param(cr, uid, 'cas_auth.cas_server', default_host)
            # Else, it seems it is the port field
            # which is empty: we save his default value
            else:
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server_port', default_port)

        # We save the field used to know
        # if users have to be created on the fly or not
        icp.set_param(
            cr, uid, 'cas_auth.cas_create_user', str(config.cas_create_user))

    def check_cas_server(self, cr, uid, ids, context=None):
        """ Check if CAS paramaters (host and port) are valids """
        title = 'cas_check_fail'
        message = 'Parameters are incorrect\nThere seems to be an \
error in the configuration.'
        config = self.browse(cr, uid, ids[0], context=context)
        if config.cas_server_port == -1:
            cas_server = config.cas_server
        else:
            url_server = urlparse(config.cas_server)
            cas_server = url_server.scheme + '://' + url_server.netloc + ':'\
                + str(config.cas_server_port) + url_server.path
        try:
            # The login function, from pycas,returns 3 if the host is
            # a CAS host and if parameters given are bad
            # (Parameters are empty, except the adress of the CAS server,
            # so there are always bad !)
            res = login(cas_server, ' ', ' ')
            if res[0] == 3:
                title = 'cas_check_success'
                message = 'Parameters are correct\nThe CAS server is well \
configured !'
        except:
            pass

        # At the moment, I only found this method
        # in order to show a message after a request
        raise osv.except_osv(_(title), _(message))
