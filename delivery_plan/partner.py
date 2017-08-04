# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv, fields


class res_partner(osv.osv):
    _inherit = "res.partner"
    
    _columns = {
        'deliver_zone':   fields.char('Delivery Zone', size= 64),
    }

res_partner()