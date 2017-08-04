# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'carrier_website': fields.related(
            'carrier_id', 'partner_id', 'website',
            type='char', string="Carrier website"),
        'tracking_website': fields.related(
            'carrier_id', 'tracking_website',
            string='Tracking Website Url', type='char'),
    }


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'carrier_website': fields.related(
            'carrier_id', 'partner_id', 'website',
            type='char', string="Carrier website"),
        'tracking_website': fields.related(
            'carrier_id', 'tracking_website',
            string='Tracking Website Url', type='char'),
    }


class delivery_carrier(orm.Model):
    _inherit = 'delivery.carrier'

    _columns = {
        'tracking_website': fields.char(
            'Tracking Website Url')
    }
