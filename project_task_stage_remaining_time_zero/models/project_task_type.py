# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    remaining_zero = fields.Boolean(
        string='Zero remaining quantity'
    )
