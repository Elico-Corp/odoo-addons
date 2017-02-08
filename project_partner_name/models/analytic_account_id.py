# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _get_partner_ref(self, proj):
        if proj.partner_id:
            if proj.partner_id.is_company and proj.partner_id.ref:
                return proj.partner_id.ref
            elif proj.partner_id.parent_id and proj.partner_id.parent_id.ref:
                return proj.partner_id.parent_id.ref
        return False

    def _get_full_names(self, elmt, level):

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

        (_, _, full_names) = iter_parent_ids(elmt, level, [])

        return full_names

    def name_get(self, cr, uid, ids, context=None):

        res = []
        if not ids:
            return res
        if isinstance(ids, (int, long)):
            ids = [ids]

        for id in ids:
            elmt = self.browse(cr, uid, id, context=context)
            full_names = self._get_full_names(elmt, 6)
            if isinstance(full_names, list) and full_names:
                project_ids = self.pool['project.project'].search(
                    cr, uid,
                    [('analytic_account_id', '=', id)],
                    context=context
                )
                if isinstance(project_ids, list) and project_ids:
                    project_obj = self.pool['project.project'].browse(
                        cr, uid,
                        project_ids[0],
                        context=context
                    )
                    partner_ref = self._get_partner_ref(project_obj)
                    if partner_ref:
                        full_names[0] = "%s - %s" % (
                            partner_ref,
                            full_names[0]
                        )
                full_names.reverse()  # order on First Root Last Leaf                
            res.append((id, ' / '.join(full_names)))

        return res
