# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_partner_ref(self, project):
        partner = project.partner_id
        return partner.is_company and partner.ref\
            or (partner.parent_id and partner.parent_id.ref or False)

    @api.multi
    def name_get(self):
        result = []
        for project in self:
            partner_ref = self._get_partner_ref(project)
            project_name = partner_ref and '%s - %s' % (
                partner_ref, project.name
            ) or project.name
            result.append((project.id, '%s' % (project_name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        projects = self.browse()
        if name:
            projects = self.search(
                ['|', ('partner_id.ref', operator, name),
                 ('partner_id.parent_id.ref', operator, name)] + args,
                                   limit=limit)
        if not projects:
            projects = self.search([('name', operator, name)] + args,
                                   limit=limit)
        return projects.name_get()
