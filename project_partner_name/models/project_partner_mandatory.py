# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.one
    @api.depends('partner_id')
    def _get_partner_ref(self):
        if self.partner_id:
            if self.partner_id.is_company:
                return self.partner_id.ref
            return self.partner_id.parent_id.ref
        return False

    @api.multi
    @api.depends('name', 'partner_id')
    def name_get(self):
        result = []
        for project in self:
            partner_ref = self._get_partner_ref()[0]
            if partner_ref:
                result.append((
                    project.id,
                    '%s - %s' % (partner_ref, project.name)))
            else:
                result.append((project.id, '%s' % (project.name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(
                [('partner_id.ref', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('partner_id.parent_id.ref', operator, name)] + args,
                limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
