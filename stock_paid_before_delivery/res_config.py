# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import fields, osv


class stock_config_settings(osv.osv_memory):
    _inherit = 'stock.config.settings'
    _columns = {
        'paid_before_delivery': fields.boolean('Must be paid before delivery')
    }
    _defaults = {
        'paid_before_delivery': True
    }
