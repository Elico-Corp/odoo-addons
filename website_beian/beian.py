# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia
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
from openerp import models, fields


class CompanyFiling(models.Model):
    _inherit = 'website'

    beian_url = fields.Char(string='ICP Beian URL')
    logo = fields.Binary(string='ICP Beian Logo')
    beian_number = fields.Char(string='ICP Beian Number')


class CompanyFilingSetting(models.TransientModel):
    _inherit = 'website.config.settings'

    beian_url = fields.Char(string='ICP Beian URL',
                            related='website_id.beian_url')
    logo = fields.Binary(string='ICP Beian Logo',
                         related='website_id.logo')
    beian_number = fields.Char(string='ICP Beian Number',
                               related='website_id.beian_number')
