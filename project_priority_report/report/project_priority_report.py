# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2014 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Sebastien Maillard
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp import tools


class ProjectPriorityReport(osv.Model):
    """ Project Priority Report """
    _name = "project.priority.report"
    _auto = False
    _description = "Project Priority Report"
    _order = 'project_id ASC, activity_type DESC, priority ASC,\
        sequence ASC, activity_id ASC'

    _columns = {
        'id': fields.integer('Id', readonly=True, help="Task id or Issue id"),
        'parent_id': fields.char('Parent', readonly=True, help="""
If this is a task, Id of the first parent task (if any).
If this is an issue, Id of the related task (if any).
"""),
        'activity_id': fields.char(
            'Activity Id', readonly=True, help="Task Id or Issue Id"),
        'activity_type': fields.selection(
            [
                ('task', 'Task'),
                ('issue', 'Issue'),
            ], 'Type', readonly=True,
            help="Type is used to separate Tasks and Issues"
        ),
        'project_id': fields.many2one(
            'project.project', 'Project', readonly=True),
        'stage_id': fields.many2one(
            'project.task.type', 'Stage', readonly=True),
        'name': fields.char('Name', readonly=True),
        'create_date': fields.date('Creation Date', readonly=True),
        'tags': fields.char('Tags', readonly=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'planned_hours': fields.float(
            'Init. time', digits=(16, 2), readonly=True, help="Initial time"),
        'remaining_hours': fields.float(
            'Remain. time', digits=(16, 2), readonly=True,
            help="Remaining time"),
        'sequence': fields.integer('Sequence', readonly=True),
        'priority': fields.integer('Priority', readonly=True),
        'ts_total': fields.float(
            'Time spent', digits=(16, 2), readonly=True,
            help="Time spent on timesheet"),
    }

    def init(self, cr):
        """
            Project Priority Report.

            @param cr: the current row, from the database cursor
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
                        t.create_date as create_date,
                        -- Aggregate tags into one column
                        string_agg(
                            -- Use DISTINCT because the link with task works
                            -- brings several lines, which results in having
                            -- the same tag brought several times
                            DISTINCT c.name,', ' ORDER BY c.name) AS tags,
                        t.stage_id,
                        tp.parent_id,
                        t.planned_hours,
                        t.remaining_hours,
                        t.user_id,
                        t.sequence,
                        t.priority::integer,
                        sum(al.unit_amount) AS ts_total
                    FROM project_task t
                    -- Link with parent task: create a table containing only
                    -- the parent with the highest ID for each task in order
                    -- to select 0 or 1 parent, even if the task has several
                    -- parents
                    LEFT OUTER JOIN (
                        SELECT max(tr.parent_id) AS parent_id, tr.task_id
                        FROM project_task_parent_rel tr
                        GROUP BY tr.task_id
                    ) AS tp ON tp.task_id = t.id
                    LEFT OUTER JOIN project_task_work tw ON tw.task_id = t.id
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
                    FROM project_issue i
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
