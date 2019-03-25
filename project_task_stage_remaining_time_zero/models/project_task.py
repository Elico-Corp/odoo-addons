# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def write(self, vals):
        if self.env['project.task.type'].browse(
                vals.get('stage_id')).remaining_zero:
            vals.update({'remaining_hours': 0})
        res = super(ProjectTask, self).write(vals)
        return res
