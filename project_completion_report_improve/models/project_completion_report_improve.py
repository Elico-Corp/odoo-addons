# -*- coding: utf-8 -*-
# © 2016 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, tools


class ProjectCompletionReportImprove(models.Model):
    _inherit = 'project.completion.report'

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
    task_category = fields.Many2one(
        'project.category', string='Task Category'
    )
    project_state = fields.Char(
        'Project state', readonly=True, help="Project State")

    @api.model_cr
    def init(self):
        """
            Project Completion Report
        """
        tools.drop_view_if_exists(self._cr, 'project_completion_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW project_completion_report AS (
                -- Since Odoo requires a unique ID for each line and since some
                -- issues and tasks might share the same ID, use the row number
                -- to ensure each row has a unique ID
                SELECT
                    row_number() OVER (ORDER BY q.activity_id) AS id, q.*
                FROM
                (
                    (
                        SELECT
                            a.partner_id,
                            b.project_id AS master_project_id,
                            b.id AS br_id,
                            b.state AS br_status,
                            t.categ_id AS task_category,
                            CASE WHEN p.active = True THEN 'Active'
                            WHEN p.active = False THEN 'Archived' 
                            END AS project_state,
                            p.id AS project_id,
                            a.id AS account_id,
                            p.project_categ_id,
                            'task' AS activity_type,
                            t.id AS activity_id,
                            t.name AS activity_name,
                            t.user_id,
                            t.stage_id AS activity_stage_id,
                            COALESCE(r.qty, 0) AS estimated_hours,
                            t.planned_hours,
                            COALESCE(SUM(al.unit_amount), 0) AS total_tms,
                            t.remaining_hours,
                            COALESCE(SUM(al.unit_amount), 0)
                                + t.remaining_hours AS total_hours,
                            COALESCE(SUM(al.unit_amount), 0)
                                + t.remaining_hours - COALESCE(r.qty, 0)
                                AS variance
                        FROM
                            project_project p
                            -- Link with the analytic account
                            INNER JOIN account_analytic_account a
                                ON a.id = p.analytic_account_id
                            -- Link with the task
                            INNER JOIN project_task t ON t.project_id = p.id
                            -- Link with the timesheet
                            LEFT OUTER JOIN account_analytic_line tw
                                ON tw.task_id = t.id
                            LEFT OUTER JOIN account_analytic_line tms
                                ON tms.id = tw.sheet_id
                            LEFT OUTER JOIN account_analytic_line al
                                ON al.id = tms.account_id
                            -- Link with the BR
                            LEFT OUTER JOIN business_requirement b
                                ON b.id = p.business_requirement_id
                            -- Link with the BR resource
                            LEFT OUTER JOIN business_requirement_resource r
                                ON r.business_requirement_id = b.id
                                AND r.id = t.br_resource_id
                        GROUP BY
                            t.id, p.id, a.id, b.id, r.id
                    )
                    UNION
                    (
                        SELECT
                            a.partner_id,
                            b.project_id AS master_project_id,
                            b.id AS br_id,
                            b.state AS br_status,
                            null as task_category,
                            CASE WHEN p.active = True THEN 'Active'
                            WHEN p.active = False THEN 'Archived' 
                            END AS project_state,
                            p.id AS project_id,
                            a.id AS account_id,
                            p.project_categ_id,
                            'issue' AS activity_type,
                            i.id AS activity_id,
                            i.name AS activity_name,
                            i.user_id,
                            i.stage_id AS activity_stage_id,
                            0 AS estimated_hours,
                            0 AS planned_hours,
                            SUM(al.unit_amount) AS total_tms,
                            0 AS remaining_hours,
                            SUM(al.unit_amount) AS total_hours,
                            SUM(al.unit_amount) AS variance
                        FROM
                            project_project p
                            -- Link with the analytic account
                            INNER JOIN account_analytic_account a
                                ON a.id = p.analytic_account_id
                            -- Link with the issue
                            INNER JOIN project_issue i ON i.project_id = p.id
                            -- Link with the timesheet
                            LEFT OUTER JOIN account_analytic_line ts
                                ON ts.issue_id = i.id
                            LEFT OUTER JOIN account_analytic_line al
                                ON al.id = ts.sheet_id
                            -- Link with the BR
                            LEFT OUTER JOIN business_requirement b
                                ON b.id = p.business_requirement_id
                        GROUP BY
                            i.id, p.id, a.id, b.id
                    )
                ) AS q)""")
