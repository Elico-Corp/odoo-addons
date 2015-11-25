# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class TaskType(models.Model):
    _name = 'task.type'

    name = fields.Char('Name', required=True, translate=True, select=True)
    parent_id = fields.Many2one('project.task', 'Parent Type', select=True)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one('task.type', 'Root Type for Tasks', readme=True)
