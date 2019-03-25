# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectProjectCategory(models.Model):
    _name = 'project.project.category'

    name = fields.Char('Name', required=True, translate=True, index=True)
    description = fields.Char('Description', translate=True)
    active = fields.Boolean('Active', default=True)

    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',
         'Name already exists.'),
    ]


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_categ_id = fields.Many2one(
        'project.project.category',
        'Project Category',
    )
