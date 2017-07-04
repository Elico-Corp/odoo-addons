# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (http://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


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

    week_1 = fields.Float('Week1', help="Time planned for week 1")
    week_2 = fields.Float('Week2', help="Time planned for week 2")
    week_3 = fields.Float('Week3', help="Time planned for week 3")
    week_4 = fields.Float('Week4', help="Time planned for week 4")
