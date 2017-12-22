# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    is_modified = fields.Boolean(
        string='Is modified',
        help='If this field is true,everyone can create the corresponding '
             'task,and if it is false, only the person in the manager group '
             'can create the corresponding task')
