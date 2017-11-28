# -*- coding: utf-8 -*-
# © 2016 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, tools


class TimesheetReportImprove(models.Model):
    _inherit = 'timesheet.activity.report'

    br_master_project = fields.Many2one(
        'project.project', string='BR Master Pro.'
    )
    br_status = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('approved', 'Approved'),
         ('stakeholder_approval', 'Stakeholder Approval'),
         ('in_progress', 'In progress'),
         ('done', 'Done'),
         ('cancel', 'Cancel'),
         ('drop', 'Drop')],
        string='BR status',
    )
    department_id = fields.Many2one('hr.department', string='Department')
    project_state = fields.Char(
        'Project state', readonly=True, help="Project State")

    def _select(self):
        select_str = """
            SELECT
                ts.id,
                 -- Check if the timesheet is linked to a task
                 -- or an issue
                CASE WHEN (select id from project_task where id = al.task_id)
                IS NOT NULL THEN 'task'
                ELSE (
                    CASE WHEN (select id from project_issue where id =
                    al.issue_id) IS NOT NULL THEN 'issue'
                    -- Timesheet created in the timesheet
                    -- activities panel
                ELSE (
                    CASE WHEN al.id IS NOT NULL THEN 'timesheet'
                    -- No timesheet attached to this
                    -- task/project/BR
                ELSE NULL
                    END
                    )
                    END
                )
                END AS activity_type,
                -- Description from the task first
                -- because the one in the timesheet
                -- is wrong when it's linked to a task
                 b.state AS br_status,
                 b.project_id AS br_master_project,
                 em.department_id AS department_id,
                 CASE WHEN p.active = True THEN 'Active'
                 WHEN p.active=False THEN 'Archived' END AS project_state,
                 COALESCE((select name from project_task where id =
                 al.task_id), al.name) AS description,
                 al.unit_amount AS hours,
                 al.user_id,
                 al.product_id,
                 al.date,
                 al.project_id,
                 COALESCE((select stage_id from project_task where id =
                 al.task_id), (select stage_id from project_issue where id =
                 al.issue_id)) AS activity_stage_id,
                 COALESCE(a.id, al.account_id) AS account_id,
                 COALESCE((select id from project_task where id = al.task_id),
                 (select id from project_issue where id = al.issue_id))
                 AS activity_id,
                 COALESCE((select name from project_task where id =
                 al.task_id), (select name from project_issue where id =
                 al.issue_id)) AS activity_name,
                 (select categ_id from project_task where id =
                 al.task_id) AS categ_id,
                 b.id AS br_id,
                 a.partner_id,
                 (select project_categ_id from project_project where id =
                 al.project_id)
        """
        return select_str

    def _from(self):
        from_str = """
        hr_timesheet_sheet_sheet ts
            LEFT OUTER JOIN account_analytic_line al
                ON ts.id = al.sheet_id
            LEFT OUTER JOIN account_analytic_account a
                ON a.id = al.account_id
            LEFT OUTER JOIN res_users ru
                ON ru.id = al.user_id
            LEFT OUTER JOIN res_partner rp
                on rp.id = ru.partner_id
            LEFT OUTER JOIN hr_employee em
                on em.name_related = rp.name
            LEFT OUTER JOIN project_project p
                on a.id = p.analytic_account_id
            LEFT OUTER JOIN business_requirement b
                ON b.id = (select business_requirement_id from project_project
                where id = al.project_id)
        """
        return from_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            )""" % (self._table, self._select(), self._from()))
