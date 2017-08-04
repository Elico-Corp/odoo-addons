# -*- coding: utf-8 -*-
# © 2011 Cubic ERP - Teradata SAC(http://cubicerp.com)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from openerp.tools.translate import _

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
        'carrier_id': fields.many2one('delivery.carrier', 'Carrier', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'dts_id': fields.many2one('delivery.time', 'Delivery Time', help='Delivery time or turn to receive', domain=[('type', '=', 'dts'), ('active', '=', True)]),
        'is_collected': fields.boolean(_('Collected ?')),
    }
purchase_order()
