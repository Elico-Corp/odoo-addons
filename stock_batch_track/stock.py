# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv
from osv import fields

class stock_track(osv.osv):
    _inherit = 'stock.tracking'
    _columns = {
        'partner_id': fields.many2one('res.partner', string='Subcontractor'),
    }
stock_track()
        
