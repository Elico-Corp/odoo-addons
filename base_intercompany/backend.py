# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import openerp.addons.connector.backend as backend


icops = backend.Backend('icops')
""" Generic ICOPS Backend """

icops7 = backend.Backend(parent=icops, version='7.0')
""" ICOPS Backend for OpenERP 7 """
