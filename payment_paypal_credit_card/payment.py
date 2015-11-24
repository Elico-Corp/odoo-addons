# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Augustin Cisterne-Kaas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
