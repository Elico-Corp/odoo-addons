# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _get_partner_ref(self, project):
        partner = project.partner_id
        return partner.is_company and partner.ref\
            or (partner.parent_id and partner.parent_id.ref or False)

    @api.multi
    def _get_full_names(self, level):
        self.ensure_one()

        # Tail recursion function
        def iter_parent_ids(elmt, level, full_names):
            if level <= 0:
                full_names.append('...')
                return (None, 0, full_names)
            elif elmt.parent_id and not elmt.type == 'template':
                full_names.append(elmt.name)
                return iter_parent_ids(elmt.parent_id, level - 1, full_names)
            else:
                full_names.append(elmt.name)
                return (None, level - 1, full_names)

        (_, _, full_names) = iter_parent_ids(self, level, [])

        return full_names

    @api.multi
    def name_get(self):
        res = []
        project_obj = self.env['project.project']
        for analytic_acc in self:
            full_names = analytic_acc._get_full_names(6)
            if isinstance(full_names, list) and full_names:
                project = project_obj.search(
                    [('analytic_account_id', '=', analytic_acc.id)], limit=1
                )
                if project:
                    partner_ref = self._get_partner_ref(project)
                    if partner_ref:
                        full_names[0] = "%s - %s" % (
                            partner_ref,
                            full_names[0]
                        )
                full_names.reverse()  # order on First Root Last Leaf
            res.append((analytic_acc.id, ' / '.join(full_names)))

        return res
