# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class ProjectWork(models.Model):
    _inherit = 'project.task.work'

    @api.model
    def create(self, vals):
        """
        When create a new record, modify the timesheet task_id field
        :param vals:
        :return:
        """
        res = super(ProjectWork, self).create(vals)
        time_sheet = res.hr_analytic_timesheet_id
        if time_sheet:
            time_sheet.task_id = vals.get('task_id', False)

        return res

    @api.multi
    def write(self, vals):
        if 'task_id' in vals:
            task_id = vals['task_id']
            for record in self:
                time_sheet = record.hr_analytic_timesheet_id
                if time_sheet:
                    time_sheet.task_id = task_id
        return super(ProjectWork, self).write(vals)


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    task_id = fields.Integer('Task ID', readonly=True)
