# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016-2018 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from odoo.exceptions import ValidationError
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _
from urllib import parse

_logger = logging.getLogger(__name__)
try:
    from ..pycas import login
except (ImportError, IOError) as err:
    _logger.debug(err)

default_host = 'https://localhost'
default_port = 8443


class CasBaseConfigSettings(models.TransientModel):
    """
    The fields declared here are used
    to manage settings of the CAS server.
    """
    _inherit = 'res.config.settings'
    cas_activated = fields.Boolean(
        'CAS authentication activated',
        help='The CAS authentication only works if you are in a single'
             ' database mode. You can launch the Odoo Server with the'
             ' option --db-filter=YOUR_DATABASE to do so.')
    cas_server = fields.Char('CAS Server address', size=64)
    cas_server_port = fields.Integer('CAS Server port')
    cas_create_user = fields.Boolean(
        'Users created on the fly',
        help='Automatically create local user accounts for'
             ' new users authenticating via CAS', default=True)

    # Getter is required for fields stored in base.config.settings
    @api.model
    def get_default_cas_values(self, fields):
        icp = self.env['ir.config_parameter']
        return {
            'cas_activated': safe_eval(
                icp.get_param('cas_auth.cas_activated', 'False')),
            'cas_server': icp.get_param('cas_auth.cas_server', default_host),
            'cas_server_port': int(
                icp.get_param('cas_auth.cas_server_port', default_port)),
            'cas_create_user': safe_eval(
                icp.get_param('cas_auth.cas_create_user', 'True')),
        }

    # Setter is required too
    @api.multi
    def set_cas_values(self):
        self.ensure_one()
        icp = self.env['ir.config_parameter']

        error = True

        # If the host AND the port are valid,
        # we can activate CAS authentication and save all values
        if self.cas_server and self.cas_server_port:
            if self.cas_activated:
                icp.set_param('cas_auth.cas_activated',
                              str(self.cas_activated))
                # There is no error
                error = False
            icp.set_param('cas_auth.cas_server', self.cas_server)
            icp.set_param('cas_auth.cas_server_port',
                          self.cas_server_port)
        # Else, there is one error
        # If the host field is valid, we save it and the default port value
        elif self.cas_server:
            icp.set_param('cas_auth.cas_server', self.cas_server)
            icp.set_param('cas_auth.cas_server_port', default_port)
        # Else, the host field is empty,
        # but not the port field: we save it and the default host value
        else:
            icp.set_param('cas_auth.cas_server_port',
                          self.cas_server_port)
            icp.set_param('cas_auth.cas_server', default_host)
        # If error is True, there is at least one error,
        # so we deactivate CAS authentication
        if error:
            icp.set_param('cas_auth.cas_activated', 'False')
            # If the host field is empty, we save his default value
            if not self.cas_server:
                icp.set_param('cas_auth.cas_server', default_host)
            # Else, it seems it is the port field
            # which is empty: we save his default value
            else:
                icp.set_param('cas_auth.cas_server_port', default_port)

        # We save the field used to know
        # if users have to be created on the fly or not
        icp.set_param('cas_auth.cas_create_user', str(self.cas_create_user))

    @api.multi
    def check_cas_server(self):

        """Check whether CAS paramaters (host and port) are valid"""

        self.ensure_one()
        title = 'cas_check_fail'
        message = 'Parameters are incorrect\nThere seems to be an ' \
                  'error in the configuration.'
        error_message = ''
        if self.cas_server_port == -1:
            cas_server = self.cas_server
        else:
            url_server = parse.urlparse(self.cas_server)
            cas_server = \
                url_server.scheme + '://' + url_server.netloc + \
                ':' + str(self.cas_server_port) + url_server.path
        try:
            # The login function, from pycas,returns 3 if the host is
            # a CAS host and if parameters given are bad
            # (Parameters are empty, except the adress of the CAS server,
            # so there are always bad !)
            res = login(cas_server, ' ', ' ')
            if res[0] == 3:
                title = 'cas_check_success'
                message = 'Parameters are correct\nThe CAS server is well ' \
                          'configured'
        except Exception as e:
            _logger.debug(e)
            error_message = e
        # At the moment, I only found this method
        # in order to show a message after a request
        raise ValidationError(_(title) + '\n' + _(message) + '\n' + _(
            error_message))
