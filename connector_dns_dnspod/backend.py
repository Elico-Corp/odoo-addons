# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.addons.connector.backend as backend
from openerp.addons.connector_dns.backend import dns

dnspod = backend.Backend(parent=dns, version='dnspod')
