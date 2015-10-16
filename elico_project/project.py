# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
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
from openerp import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    type = fields.Selection(
        [('ADM', 'ADM'),
         ('DEV', 'DEV'),
         ('FS', 'FS'),
         ('PM', 'PM'),
         ('QA', 'QA'),
         ('SAL', 'SAL'),
         ('TR', 'TR'),
         ('TS', 'TS')],
        string='Type', required=True, help="""
        Type of task. Following values are available:
            - ADM: administrative task
            - DEV: development task
            - FS: functional specification task
            - PM: project managment task
            - QA: quality control task
            - SAL: sales task
            - TR: training task
            - TS: technical specification task
        """)

    wbs = fields.Char('WBS', help="Work Breakdown Structure")

    week_1 = fields.Float('Week1', help="Time planned for the current week")
    week_2 = fields.Float('Week2', help="Time planned for next week")
    week_3 = fields.Float('Week3', help="Time planned in 2 weeks")
    week_4 = fields.Float('Week4', help="Time planned in 3 weeks")

    # Siyuan: 8019 Make Project field mandatory for tasks and issues
    project_id = fields.Many2one(required=True)


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    # Siyuan: 8019 Make Project field mandatory for tasks and issues
    project_id = fields.Many2one(required=True)
