# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class ProjectInherit(models.Model):
    _inherit = 'project.project'

    check_timesheet = fields.Boolean(
        string="Check TMS",
        default=True,
        help='If true, the TMS will be assigned to the manager of the'
             ' employee,if false, the TMS will be assigned to the manager '
             'of the project.')
