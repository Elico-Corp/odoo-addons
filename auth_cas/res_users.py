# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, osv
from openerp.exceptions import AccessDenied

import logging

_logger = logging.getLogger(__name__)


class res_users(osv.osv):
    """
    The field declared here is used in order to check autenticity of logins
    """
    _inherit = 'res.users'

    _columns = {
        'cas_key': fields.char('CAS Key', size=16, readonly=True),
    }

    def check_credentials(self, cr, uid, password):
        """ Check autenticity of logins """
        # We try to connect the user with his password by the standard way
        try:
            return super(res_users, self).check_credentials(cr, uid, password)
        # If it failed, we try to do it thanks to
        # the cas key created by the Controller
        except AccessDenied:
            if not password:
                raise AccessDenied()
            cr.execute("""SELECT COUNT(1)
                                FROM res_users
                               WHERE id=%s
                                 AND cas_key=%s""",
                       (int(uid), password))
            if not cr.fetchone()[0]:
                raise AccessDenied()
