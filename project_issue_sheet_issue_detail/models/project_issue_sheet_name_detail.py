# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def name_get(self):
        result = []
        values = super(AccountAnalyticLine, self).name_get()
        id_name_dict = {}
        for record in self:
            if record.issue_id:
                issue_record = record.issue_id
                issue_name = issue_record.name
                issue_id = issue_record.id
                id_name_dict[record.id] = 'I%s-%s: %s' % \
                                          (issue_id, issue_name, record.name)
        for r_id, display_name in values:
            if r_id in id_name_dict:
                display_name = id_name_dict[r_id]
            result.append((r_id, display_name))
        return result
