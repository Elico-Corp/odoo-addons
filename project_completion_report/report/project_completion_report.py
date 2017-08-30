# -*- coding: utf-8 -*-
# © 2016 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, tools


class ProjectCompletionReport(models.Model):
    """
        Project Completion Report
    """
    _name = "project.completion.report"
    # Database table should not be created, use init() instead
    _auto = False
    _description = "Project Completion Report"
    # Field used for the Name
    _rec_name = 'activity_name'

    id = fields.Integer('Id', readonly=True)
    activity_type = fields.Selection(
        [
            ('task', 'Task'),
            ('issue', 'Issue'),
        ], 'Type', readonly=True,
        help="Type is used to separate Tasks and Issues")
    hours = fields.Float(
        'Time spent', digits=(16, 2), readonly=True,
        help="Time spent on timesheet")
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    project_id = fields.Many2one(
        'project.project', 'Project', readonly=True)
    project_state = fields.Char(
        'State', readonly=True, help="Project State")
    activity_stage_id = fields.Many2one(
        'project.task.type', 'Stage',
        readonly=True, help="Activity Stage")
    account_id = fields.Many2one(
        'account.analytic.account', 'Analytic account', readonly=True)
    activity_id = fields.Char(
        'Activity id', readonly=True, help="Task id or Issue id")
    activity_name = fields.Char(
        'Activity name', readonly=True, help="Task name or Issue name")

    # FIXME There should be a link between resource and task. If the link
    # existed, each task would have either:
    #  - 0 estimated hour (task created manually)
    #  - estimated hours of the corresponding resource
    # Since the link doesn't exist, the estimated hours of each task is
    # currently the average of the estimated hours of all the resources.
    # The other problem is that if there are tasks created manually, they will
    # also have the same estimated hours, meaning the total estimated hours of
    # a BR will be more than the total estimated hours of its resources. A
    # workaround would be to divide by the number of tasks and multiply by the
    # number of resources. All this wouldn't happen if there was the link.
    estimated_hours = fields.Float(
        'Est. time', digits=(16, 2), readonly=True,
        help="Estimated time (from BR)")

    planned_hours = fields.Float(
        'Init. time', digits=(16, 2), readonly=True,
        help="Initial time (from Task)")
    remaining_hours = fields.Float(
        'Remain. time', digits=(16, 2), readonly=True,
        help="Remaining time")
    br_id = fields.Many2one(
        'business.requirement', 'Bus. requ.',
        readonly=True, help="Business requirement")
    partner_id = fields.Many2one(
        'res.partner', 'Customer', readonly=True)
    project_categ_id = fields.Many2one(
        'project.project.category',
        'Project Cat.', readonly=True, help="Project Category")

    def init(self, cr):
        """
            Project Completion Report
        """
        tools.drop_view_if_exists(cr, 'project_completion_report')
        cr.execute("""
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
                            'task' AS activity_type,
                            SUM(al.unit_amount) AS hours,
                            t.user_id,
                            p.id AS project_id,
                            p.state AS project_state,
                            t.stage_id AS activity_stage_id,
                            a.id AS account_id,
                            t.id AS activity_id,
                            t.name AS activity_name,
                            AVG(r.qty) AS estimated_hours,
                            t.planned_hours,
                            t.remaining_hours,
                            b.id AS br_id,
                            a.partner_id,
                            p.project_categ_id
                        FROM
                            project_project p
                            -- Link with the analytic account
                            INNER JOIN account_analytic_account a
                                ON a.id = p.analytic_account_id
                            -- Link with the task
                            INNER JOIN project_task t ON t.project_id = p.id
                            -- Link with the timesheet
                            LEFT OUTER JOIN project_task_work tw
                                ON tw.task_id = t.id
                            LEFT OUTER JOIN hr_analytic_timesheet ts
                                ON ts.id = tw.hr_analytic_timesheet_id
                            LEFT OUTER JOIN account_analytic_line al
                                ON al.id = ts.line_id
                            -- Link with the BR
                            LEFT OUTER JOIN business_requirement b
                                ON b.id = p.business_requirement_id
                            -- Link with the BR resources
                            LEFT OUTER JOIN business_requirement_resource r
                                ON r.business_requirement_id = b.id
                        GROUP BY
                            t.id, p.id, a.id, b.id
                    )
                    UNION
                    (
                        SELECT
                            'issue' AS activity_type,
                            SUM(al.unit_amount) AS hours,
                            i.user_id,
                            p.id AS project_id,
                            p.state AS project_state,
                            i.stage_id AS activity_stage_id,
                            a.id AS account_id,
                            i.id AS activity_id,
                            i.name AS activity_name,
                            NULL AS estimated_hours,
                            NULL AS planned_hours,
                            NULL AS remaining_hours,
                            b.id AS br_id,
                            a.partner_id,
                            p.project_categ_id
                        FROM
                            project_project p
                            -- Link with the analytic account
                            INNER JOIN account_analytic_account a
                                ON a.id = p.analytic_account_id
                            -- Link with the issue
                            INNER JOIN project_issue i ON i.project_id = p.id
                            -- Link with the timesheet
                            LEFT OUTER JOIN hr_analytic_timesheet ts
                                ON ts.issue_id = i.id
                            LEFT OUTER JOIN account_analytic_line al
                                ON al.id = ts.line_id
                            -- Link with the BR
                            LEFT OUTER JOIN business_requirement b
                                ON b.id = p.business_requirement_id
                        GROUP BY
                            i.id, p.id, a.id, b.id
                    )
                ) AS q)""")

