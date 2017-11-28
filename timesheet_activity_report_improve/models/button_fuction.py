# -*- coding: utf-8 -*-
# © 2016 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, tools, _


class BRButtonFunction(models.Model):
    _inherit = "business.requirement"

    @api.multi
    def br_open_tms_activity_report(self):
        for record in self:
            domain = [('br_id', '=', record.id)]
            return {
                'name': _('BR_timesheet_activity_report'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'graph',
                'res_model': 'timesheet.activity.report',
                'target': 'current',
                'domain': domain,
            }


class ProjectButtonFunction(models.Model):
    _inherit = "project.project"

    @api.multi
    def project_open_tms_activity_rep(self):
        for record in self:
            domain = [('project_id', '=', record.id)]
            return {
                'name': _('Project_timesheet_activity_report'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'graph',
                'res_model': 'timesheet.activity.report',
                'target': 'current',
                'domain': domain,
            }
