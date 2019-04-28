# 2016-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class CompanyShop(models.Model):
    _name = 'company.shop'

    name = fields.Char('Name', required=True)
    city = fields.Char('City', required=True)
    address = fields.Char('Address', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company')


class ResCompany(models.Model):
    _inherit = 'res.company'

    shop_ids = fields.One2many(
        comodel_name='company.shop', inverse_name='company_id', string='shop')
