# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ldap
from odoo import models


class CompanyLdap(models.Model):
    _inherit = 'res.company.ldap'

    def connect(self, conf):
        connection = super(CompanyLdap, self).connect(conf)
        # authorize self signed certificate
        if conf['ldap_tls']:
            connection.set_option(
                ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
        return connection
