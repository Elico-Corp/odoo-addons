# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class AcquirerPaypal(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _get_icons(self):
        # getting default icons from providers list.
        # since we do not want to add a new provider
        providers = self._get_providers()
        providers.append(['paypal_credit_card', 'Paypal Credit card'])
        return providers

    icon = fields.Selection(_get_icons, string="Icon")
