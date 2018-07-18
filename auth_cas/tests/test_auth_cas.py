# -*- coding: utf-8 -*-
# © 2018 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common
from mock import patch
from odoo.addons.auth_cas.controllers.main import Controller


class TestAuthCas(common.TransactionCase):

    def setUp(self):
        """Create a packaging and wac."""
        super(TestAuthCas, self).setUp()

    @patch('odoo.addons.auth_cas.controllers.main.request')
    @patch('odoo.http.request')
    def test_auth_cas(self, request, request2):
        """Move stages for Tasks and Issues."""
        controller_ref = Controller()

        controller_ref.cas_authenticate()
