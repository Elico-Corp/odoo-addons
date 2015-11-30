# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProjectType(models.Model):
    _name = 'task.category'

    name = fields.Char('Name', translate=True, select=True)
    description = fields.Char('Description', translate=True)

    _order = 'name'


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one(
        'task.category',
        'Type for Tasks',
        required=True,
    )
