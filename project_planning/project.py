# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    week_1 = fields.Float('Week1', help="Time planned for the current week")
    week_2 = fields.Float('Week2', help="Time planned for next week")
    week_3 = fields.Float('Week3', help="Time planned for week 3")
    week_4 = fields.Float('Week4', help="Time planned for week 4")

