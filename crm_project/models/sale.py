# -*- coding: utf-8 -*-
from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    crm_project_id = fields.Many2one('project.project', string='Project')
