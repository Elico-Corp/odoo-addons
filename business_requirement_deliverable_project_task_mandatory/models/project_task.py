# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    br_required = fields.Boolean(
        related='project_id.project_categ_id.br_required',
        readonly=True,
    )

    @api.constrains(
        'project_id',
        'business_requirement_id',
        'br_required')
    def _check_br_required(self):
        for t in self:
            if t.br_required and not t.business_requirement_id.id:
                raise models.ValidationError(
                    'The Business Requirement is mandatory'
                    ' for this type of project category')
