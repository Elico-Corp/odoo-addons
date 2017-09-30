# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, tools


class ProjectPriorityReport(models.Model):
    """
        Project Priority Report.
    """
    _name = "project.priority.report"
    # Database table should not be created, use init() instead
    _auto = False
    _description = "Project Priority Report"
    _order = ('project_id ASC, activity_type DESC, priority ASC, '
              'sequence ASC, activity_id ASC')

    id = fields.Integer('Id', readonly=True, help="Task id or Issue id")
    parent_id = fields.Char(
        'Parent', readonly=True,
        help="If this is a task, Id of the first parent task (if any). "
             "If this is an issue, Id of the related task (if any).")
    activity_id = fields.Char(
        'Activity Id', readonly=True, help="Task Id or Issue Id")
    activity_type = fields.Selection(
        [
            ('task', 'Task'),
            ('issue', 'Issue'),
        ], 'Type', readonly=True,
        help="Type is used to separate Tasks and Issues")
    project_id = fields.Many2one(
        'project.project', 'Project', readonly=True)
    stage_id = fields.Many2one(
        'project.task.type', 'Stage', readonly=True)
    name = fields.Char('Name', readonly=True)
    create_date = fields.Date('Creation Date', readonly=True)
    tags = fields.Char('Tags', readonly=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    planned_hours = fields.Float(
        'Init. time', digits=(16, 2), readonly=True, help="Initial time")
    remaining_hours = fields.Float(
        'Remain. time', digits=(16, 2), readonly=True,
        help="Remaining time")
    sequence = fields.Integer('Sequence', readonly=True)
    priority = fields.Integer('Priority', readonly=True)
    tms_total = fields.Float(
        'Time spent', digits=(16, 2), readonly=True,
        help="Time spent on timesheet")

    def init(self, cr):
        """
            Project Priority Report.
        """
        tools.drop_view_if_exists(cr, 'project_priority_report')
        cr.execute("""
            CREATE OR REPLACE VIEW project_priority_report AS (
                -- Since Odoo requires a unique ID for each line and since some
                -- issues and tasks might share the same ID, use the row number
                -- to ensure each row has a unique ID
                SELECT row_number() OVER (ORDER BY q.activity_id) AS id, q.*
                FROM (
                    SELECT
                        t.id AS activity_id,
                        'task' AS activity_type,
                        t.project_id,
                        t.name,
                        t.create_date AS create_date,
                        -- Aggregate tags into one column
                        string_agg(
                            -- Use DISTINCT because the link with task works
                            -- brings several lines, which results in having
                            -- the same tag brought several times
                            DISTINCT c.name, ', ' ORDER BY c.name) AS tags,
                        t.stage_id,
                        tp.parent_id,
                        t.planned_hours,
                        t.remaining_hours,
                        t.user_id,
                        t.sequence,
                        t.priority::integer,
                        sum(al.unit_amount) AS tms_total
                    FROM
                        project_task t
                        -- Link with parent task: create a table containing
                        -- only the parent with the highest ID for each task in
                        -- order to select 0 or 1 parent, even if the task has
                        -- several parents
                        LEFT OUTER JOIN (
                            SELECT max(tr.parent_id) AS parent_id, tr.task_id
                            FROM project_task_parent_rel tr
                            GROUP BY tr.task_id
                        ) AS tp ON tp.task_id = t.id
                        LEFT OUTER JOIN project_task_work tw
                            ON tw.task_id = t.id
                        LEFT OUTER JOIN hr_analytic_timesheet ts
                            ON ts.id = tw.hr_analytic_timesheet_id
                        LEFT OUTER JOIN account_analytic_line al
                            ON al.id = ts.line_id
                        LEFT OUTER JOIN project_category_project_task_rel cr
                            ON cr.project_task_id = t.id
                        LEFT OUTER JOIN project_category c
                            ON c.id = cr.project_category_id
                    GROUP BY t.id, tp.parent_id
                UNION
                    SELECT
                        i.id AS activity_id,
                        'issue' AS activity_type,
                        i.project_id,
                        i.name,
                        i.create_date,
                        -- Aggregate tags into one column
                        string_agg(
                            -- Use DISTINCT because the link with task works
                            -- brings several lines, which results in having
                            -- the same tag brought several times
                            DISTINCT c.name,', ' ORDER BY c.name) AS tags,
                        i.stage_id,
                        i.task_id AS parent_id,
                        '0' AS planned_hours,
                        '0' AS remaining_hours,
                        i.user_id,
                        '0',
                        i.priority::integer,
                        sum(al.unit_amount) AS ts_total
                    FROM
                        project_issue i
                        LEFT OUTER JOIN hr_analytic_timesheet ts
                            ON ts.issue_id = i.id
                        LEFT OUTER JOIN account_analytic_line al
                            ON al.id = ts.line_id
                        LEFT OUTER JOIN project_category_project_issue_rel cr
                            ON cr.project_issue_id = i.id
                        LEFT OUTER JOIN project_category c
                            ON c.id = cr.project_category_id
                    GROUP BY i.id
                ) as q)""")
