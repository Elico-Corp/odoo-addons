# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    task_type_id = fields.Many2one('project.type', 'Root type for Tasks')


class ProjectType(models.Model):
    _name = 'project.type'

    name = fields.Char('Name', translate=True, select=True)
    description = fields.Char('Description', translate=True)

    _order = 'name'


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one(
        'project.type',
        'Root Type for Tasks',
        related='project_id.task_type_id')
