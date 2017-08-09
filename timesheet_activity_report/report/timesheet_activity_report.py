# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, tools


class TimesheetReport(models.Model):
    """
        Timesheet Activities Report.
    """
    _name = "timesheet.activity.report"
    _auto = False # Database table should not be created, use init() instead
    _description = "Timesheet Activities Report"
    _rec_name = 'activity_name' # Field used for the Name

    id = fields.Integer('Id', readonly=True)
    activity_type = fields.Selection(
        [
            ('task', 'Task'),
            ('issue', 'Issue'),
            ('timesheet', 'Timesheet'),
        ], 'Type', readonly=True,
        help="Type is used to separate Tasks, Issues and " \
            "Timesheets input directly")
    description = fields.Char('Description', readonly=True)
    hours = fields.Float(
        'Time spent', digits=(16, 2), readonly=True,
        help="Time spent on timesheet")
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    date = fields.Date('Date', readonly=True)
    project_id = fields.Many2one('project.project', 'Project', readonly=True)
    project_state = fields.Char('State', readonly=True, help="Project State")
    activity_stage_id = fields.Many2one(
        'project.task.type', 'Stage',
        readonly=True, help="Activity Stage")
    account_id = fields.Many2one(
            'account.analytic.account', 'Analytic account', readonly=True)
    activity_id = fields.Char(
            'Activity id', readonly=True, help="Task id or Issue id")
    activity_name = fields.Char(
            'Activity name', readonly=True, help="Task name or Issue name")
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
            Timesheet Activities Report.
        """
        tools.drop_view_if_exists(cr, 'timesheet_activity_report')
        cr.execute("""
            CREATE OR REPLACE VIEW timesheet_activity_report AS (
                SELECT
                    ts.id,
                    -- Check if the timesheet is linked to a task
                    -- or an issue
                    CASE WHEN tw.id IS NOT NULL THEN 'task'
                    ELSE (
                        CASE WHEN i.id IS NOT NULL THEN 'issue'
                        -- Timesheet created in the timesheet
                        -- activities panel
                        ELSE (
                            CASE WHEN ts.id IS NOT NULL THEN 'timesheet'
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
                    COALESCE(tw.name, al.name) AS description,
                    al.unit_amount AS hours,
                    al.user_id,
                    al.product_id,
                    al.date,
                    p.id AS project_id,
                    p.state AS project_state,
                    COALESCE(t.stage_id, i.stage_id) AS activity_stage_id,
                    COALESCE(a.id, al.account_id) AS account_id,
                    COALESCE(t.id, i.id) AS activity_id,
                    COALESCE(t.name, i.name) AS activity_name,
                    b.id AS br_id,
                    a.partner_id,
                    p.project_categ_id
                FROM
                    hr_analytic_timesheet ts
                    INNER JOIN account_analytic_line al
                        ON al.id = ts.line_id
                    -- Link with the task
                    LEFT OUTER JOIN project_task_work tw
                        ON tw.hr_analytic_timesheet_id = ts.id
                    LEFT OUTER JOIN project_task t ON t.id = tw.task_id
                    -- Link with the issue
                    LEFT OUTER JOIN project_issue i ON i.id = ts.issue_id
                    -- Link with the project
                    LEFT OUTER JOIN project_project p
                        ON p.id = COALESCE(t.project_id, i.project_id)
                    -- Link with the analytic account
                    LEFT OUTER JOIN account_analytic_account a
                        ON a.id = p.analytic_account_id
                    -- Link with the BR
                    LEFT OUTER JOIN business_requirement b
                        ON b.linked_project = p.id
            )""")
