# -*- coding: utf-8 -*-
# Copyright 2015-2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, tools


class TimesheetReport(models.Model):
    """
        Timesheet Activities Report.
    """
    _name = "timesheet.activity.report"
    # Database table should not be created, use init() instead
    _auto = False
    _description = "Timesheet Activities Report"
    # Field used for the Name
    _rec_name = 'activity_name'

    id = fields.Integer(
        'Id',
        readonly=True
    )
    activity_type = fields.Selection(
        [('task', 'Task'),
         ('issue', 'Issue'),
         ('timesheet', 'Timesheet'),
         ],
        'Type',
        readonly=True,
        help="""Type is based on the origin of the input (Task, Issue or
             Timesheet Activities)"""
    )
    description = fields.Char(
        'Description',
        readonly=True
    )
    hours = fields.Float(
        'Time spent',
        digits=(16, 2),
        readonly=True,
        help="Time spent on timesheet"
    )
    user_id = fields.Many2one(
        'res.users',
        'User',
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        readonly=True
    )
    date = fields.Date(
        'Date',
        readonly=True
    )
    project_id = fields.Many2one(
        'project.project',
        'Project',
        readonly=True
    )
    activity_stage_id = fields.Many2one(
        'project.task.type',
        'Activity stage',
        readonly=True,
        help="Activity Stage"
    )
    account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic account',
        readonly=True
    )
    activity_id = fields.Char(
        'Activity id',
        readonly=True,
        help="Task id or Issue id"
    )
    activity_name = fields.Char(
        'Activity name',
        readonly=True,
        help="Task name or Issue name"
    )
    categ_id = fields.Many2one(
        'project.category',
        'Task Cat.',
        readonly=True,
        help="Task Category"
    )
    br_id = fields.Many2one(
        'business.requirement',
        'Bus. requ.',
        readonly=True,
        help="Business requirement"
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Stakeholder',
        readonly=True
    )
    project_categ_id = fields.Many2one(
        'project.project.category',
        'Project Cat.',
        readonly=True,
        help="Project Category"
    )

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
