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


class TimesheetReport(osv.Model):
    """ Timesheet Activities Report """
    _name = "timesheet.activity.report"
    _auto = False
    _description = "Timesheet Activities Report"
    _rec_name = 'activity_name'

    _columns = {
        'id': fields.integer('Id', readonly=True),
        'activity_type': fields.selection(
            [
                ('task', 'Task'),
                ('issue', 'Issue'),
                ('timesheet', 'Timesheet'),
            ], 'Type', readonly=True,
            help="Type is used to separate Tasks, Issues and\
                Timesheets input directly"),
        'description': fields.char('Description', readonly=True),
        'hours': fields.float(
            'Time spent', digits=(16, 2), readonly=True,
            help="Time spent on timesheet"),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'product_id': fields.many2one(
            'product.product', 'Product', readonly=True),
        'date': fields.date('Date', readonly=True),
        'project_id': fields.many2one(
            'project.project', 'Project', readonly=True),
        'stage_id': fields.many2one(
            'project.task.type', 'Stage', readonly=True),
        'account_id': fields.many2one(
            'account.analytic.account', 'Analytic account', readonly=True),
        'activity_id': fields.char(
            'Activity id', readonly=True, help="Task id or Issue id"),
        'activity_name': fields.char(
            'Activity name', readonly=True, help="Task name or Issue name"),
        'planned_hours': fields.float(
            'Init. time', digits=(16, 2), readonly=True, help="Initial time"),
        'remaining_hours': fields.float(
            'Remain. time', digits=(16, 2), readonly=True,
            help="Remaining time"),
    }

    def init(self, cr):
        """
            Timesheet Activities Report.

            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'timesheet_activity_report')
        cr.execute("""
            CREATE OR REPLACE VIEW timesheet_activity_report AS (
                SELECT
                    ts.id as id,
                    -- Check if the timesheet is linked to a task or an issue
                    CASE WHEN tw.id IS NOT NULL THEN 'task'
                    ELSE (
                        CASE WHEN i.id IS NOT NULL THEN 'issue'
                        -- Timesheet created in the timesheet activities panel
                        ELSE 'timesheet'
                        END
                    )
                    END AS activity_type,
                    -- Description from the task first because the one in the
                    -- timesheet is wrong when it's linked to a task
                    COALESCE(tw.name, al.name) AS description,
                    al.unit_amount AS hours,
                    al.user_id,
                    al.product_id,
                    al.date,
                    COALESCE(t.project_id, i.project_id) AS project_id,
                    COALESCE(t.stage_id, i.stage_id) AS stage_id,
                    al.account_id,
                    COALESCE(t.id, i.id) AS activity_id,
                    COALESCE(t.name, i.name) AS activity_name,
                    -- The hours are null in case the timesheet is not linked
                    -- to a task
                    t.planned_hours,
                    t.planned_hours - t.effective_hours AS remaining_hours
                FROM
                    hr_analytic_timesheet ts
                    INNER JOIN account_analytic_line al ON al.id = ts.line_id
                    -- Link with the task
                    LEFT OUTER JOIN project_task_work tw
                        ON tw.hr_analytic_timesheet_id = ts.id
                    LEFT OUTER JOIN project_task t ON t.id = tw.task_id
                    -- Link with the issue
                    LEFT OUTER JOIN project_issue i ON i.id = ts.issue_id
            )""")
