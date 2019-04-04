# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import ldap
from odoo import models


class CompanyLdap(models.Model):
    _inherit = 'res.company.ldap'

    def _connect(self, conf):
        connection = super(CompanyLdap, self)._connect(conf)
        # authorize self signed certificate
        import pdb; pdb.set_trace()
        if conf['ldap_tls']:
            connection.set_option(
                ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
        return connection
