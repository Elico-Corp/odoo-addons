# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class res_users(Model):
    _inherit = 'res.users'

    # Custom Function Section
    def change_current_company(self, cr, uid, company_id, context=None):
        return self.write(cr, uid, uid, {'company_id': company_id})
