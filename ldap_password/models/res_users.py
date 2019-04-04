# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from ldap.filter import filter_format

import logging
_logger = logging.getLogger(__name__)

try:
    import ldap
except ImportError:
    _logger.debug('Can not `import ldap`.')


class res_users(models.Model):
    _inherit = 'res.users'

    @api.model
    def change_password(self, old_passwd, new_passwd):
        """Change current user password. Old password must be provided
        explicitly to prevent hijacking an existing user session, or for cases
        where the cleartext password is not used to authenticate requests.

        :return: True
        :raise: openerp.exceptions.AccessDenied when old password is wrong
        :raise: except_osv when new password is not set or empty
        """
        res = super(res_users, self).change_password(old_passwd, new_passwd)
        if res:
            user = self.env.user
            ldap_obj = self.env['res.company.ldap']
            for conf in ldap_obj._get_ldap_dicts():
                res = ldap_obj.change_password(
                    conf, user.login, old_passwd, new_passwd)
        return res


class CompanyLdap(models.Model):
    _inherit = 'res.company.ldap'

    def change_password(self, conf, login, old_passwd, new_passwd):
        conn = self._connect(conf)
        mod_attrs = [
            (ldap.MOD_REPLACE, 'userPassword', [bytes(new_passwd,'utf-8')])
        ]
        try:
            conn.simple_bind_s(conf['ldap_binddn'], conf['ldap_password'])
            ldap_filter = filter_format(conf['ldap_filter'], (login,))
            results = self._query(conf, ldap_filter)
            # Get rid of (None, attrs) for searchResultReference replies
            results = [i for i in results if i[0]]
            if results and len(results) == 1:
                # log as the current user
                conn.simple_bind_s(results[0][0], old_passwd)
                conn.modify_s(results[0][0], mod_attrs)
        except ldap.LDAPError as e:
            _logger.error('An LDAP exception occurred: %s', e)
        return True
