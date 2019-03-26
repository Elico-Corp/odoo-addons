# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, tools


class ProjectCompletionReport(models.Model):
    """Project Completion Report"""

    _name = "project.completion.report"
    # Database table should not be created, use init() instead
    _auto = False
    _description = "Project Completion Report"
    # Field used for the Name
    _rec_name = 'activity_name'

    id = fields.Integer('ID', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', 'Customer', readonly=True)
    master_project_id = fields.Many2one(
        'project.project', 'Master Project', readonly=True,
        help="Master Project of the Business Requirement")
    br_id = fields.Many2one(
        'business.requirement', 'Bus. Req.',
        readonly=True, help="Business Requirement")
    project_id = fields.Many2one(
        'project.project', 'Project', readonly=True)
    account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', readonly=True)
    project_state = fields.Char(
        'State', readonly=True, help="Project State")
    project_categ_id = fields.Many2one(
        'project.project.category',
        'Project Cat.', readonly=True, help="Project Category")
    activity_type = fields.Selection(
        [
            ('task', 'Task'),
            ('issue', 'Issue'),
        ], 'Type', readonly=True,
        help="Type is used to separate Tasks and Issues")
    activity_id = fields.Char(
        'Activity ID', readonly=True, help="Task ID or Issue ID")
    activity_name = fields.Char(
        'Activity Name', readonly=True, help="Task name or Issue name")
    user_id = fields.Many2one(
        'res.users',
        'Assignee',
        readonly=True,
        help="Assignee is not necessarily the one who input the Timesheets")
    activity_stage_id = fields.Many2one(
        'project.task.type', 'Stage',
        readonly=True, help="Activity Stage")
    # FIXME if BR resource UoM is not hours, `qty` needs to be converted
    estimated_hours = fields.Float(
        'Est. time', digits=(16, 2), readonly=True,
        help="Estimated time (from BR)")
    planned_hours = fields.Float(
        'Init. time', digits=(16, 2), readonly=True,
        help="Initial time (from Task)")
    total_tms = fields.Float(
        'Time spent', digits=(16, 2), readonly=True,
        help="Time spent on timesheet")
    remaining_hours = fields.Float(
        'Remain. time', digits=(16, 2), readonly=True,
        help="Remaining time")
    total_hours = fields.Float('Total time', digits=(16, 2), readonly=True)
    variance = fields.Float(
        'Variance', digits=(16, 2), readonly=True,
        help="Variance between Estimated time (from BR) and Total time")

    def init(self, cr):
        """Project Completion Report"""
        tools.drop_view_if_exists(cr, 'project_completion_report')
        cr.execute("""
            CREATE OR REPLACE VIEW project_completion_report AS (
                -- Since Odoo requires a unique ID for each line and since some
                -- issues and tasks might share the same ID, use the row number
                -- to ensure each row has a unique ID
                SELECT
                    row_number() OVER
                    (
                        -- Tasks first, then issues
                        -- Warning: without the sort over the activity type,
                        -- Odoo is confusing some task IDs as if they were
                        -- issue IDs
                        ORDER BY q.activity_type DESC, q.activity_id ASC
                    ) AS id, q.*
                FROM
                (
                    (
                        SELECT
                            a.partner_id,
                            b.project_id AS master_project_id,
                            b.id AS br_id,
                            p.id AS project_id,
                            a.id AS account_id,
                            p.project_categ_id,
                            p.state AS project_state,
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
                            LEFT OUTER JOIN account_analytic_line al
                                ON al.task_id = t.id
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
                            p.id AS project_id,
                            a.id AS account_id,
                            p.project_categ_id,
                            p.state AS project_state,
                            'issue' AS activity_type,
                            h.id AS activity_id,
                            h.name AS activity_name,
                            h.user_id,
                            h.stage_id AS activity_stage_id,
                            0 AS estimated_hours,
                            0 AS planned_hours,
                            COALESCE(SUM(al.unit_amount), 0) AS total_tms,
                            0 AS remaining_hours,
                            COALESCE(SUM(al.unit_amount), 0) AS total_hours,
                            COALESCE(SUM(al.unit_amount), 0) AS variance
                        FROM
                            project_project p
                            -- Link with the analytic account
                            INNER JOIN account_analytic_account a
                                ON a.id = p.analytic_account_id
                            -- Link with the issue
                            INNER JOIN helpdesk_ticket h
                                ON h.project_id = p.id
                            LEFT OUTER JOIN account_analytic_line al
                                ON al.id = tms.line_id
                            -- Link with the BR
                            LEFT OUTER JOIN business_requirement b
                                ON b.id = p.business_requirement_id
                        GROUP BY
                            i.id, p.id, a.id, b.id
                    )
                ) AS q)""")
