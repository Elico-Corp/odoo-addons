# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.osv import orm
from ldap.filter import filter_format
_logger = logging.getLogger(__name__)

try:
    import ldap
except ImportError:
    _logger.debug('Can not `import ldap`.')


class res_users(orm.Model):
    _inherit = 'res.users'

    def change_password(self, cr, uid, old_passwd, new_passwd, context=None):
        """Change current user password. Old password must be provided explicitly
        to prevent hijacking an existing user session, or for cases where the
        cleartext
        password is not used to authenticate requests.

        :return: True
        :raise: openerp.exceptions.AccessDenied when old password is wrong
        :raise: except_osv when new password is not set or empty
        """
        res = super(res_users, self).change_password(
            cr, uid, old_passwd, new_passwd, context=context)
        if res:
            user = self.browse(cr, uid, uid, context=context)
            ldap_obj = self.pool.get('res.company.ldap')
            for conf in ldap_obj.get_ldap_dicts(cr):
                res = ldap_obj.change_password(
                    conf, user.login, old_passwd, new_passwd)
            user.write({'password': None}, context=context)
        return res


class CompanyLdap(orm.Model):
    _inherit = 'res.company.ldap'

    def change_password(self, conf, login, old_passwd, new_passwd):
        conn = self.connect(conf)
        mod_attrs = [
            (ldap.MOD_REPLACE, 'userPassword', new_passwd)
        ]
        try:
            conn.simple_bind_s(conf['ldap_binddn'], conf['ldap_password'])
            filter = filter_format(conf['ldap_filter'], (login,))
            results = self.query(conf, filter)
            # Get rid of (None, attrs) for searchResultReference replies
            results = [i for i in results if i[0]]
            if results and len(results) == 1:
                # log as the current user
                conn.simple_bind_s(results[0][0], old_passwd)
                conn.modify_s(results[0][0], mod_attrs)
        except ldap.LDAPError, e:
            _logger.error('An LDAP exception occurred: %s', e)
        return True
