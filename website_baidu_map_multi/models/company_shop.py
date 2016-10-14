# -*- coding: utf-8 -*-
#   2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class CompanyShop(models.Model):
    _name = 'company.shop'

    name = fields.Char(string='Name', required=True)
    city = fields.Char(string='City', required=True)
    address = fields.Char(string='Address', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company')


class ResCompany(models.Model):
    _inherit = 'res.company'

    shop_ids = fields.One2many(
        comodel_name='company.shop', inverse_name='company_id', string='shop')
