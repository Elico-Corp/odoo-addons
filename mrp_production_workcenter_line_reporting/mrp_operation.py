# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class MrpOperations(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    reporting_ids = fields.One2many(
        'mrp.workcenter.line.reporting', 'workcenter_line_id',
        readonly=True
    )
