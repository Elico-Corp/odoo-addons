# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields
from openerp.tools.translate import _


class ProductProduct(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'licensor_ids': fields.many2many(
            'res.partner', 'product_licensor_rel', 'product_id', 'licensor_id',
            'Licensors'),
    }


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'is_licensor': fields.boolean(
            'Is Licensor',
            groups="product_licensor.group_licensor_manager"),
        'number_of_samples': fields.integer(
            'Number of samples to send',
            groups="product_licensor.group_licensor_manager"),
        'contract_number': fields.char(
            'Contract Number', size=125,
            groups="product_licensor.group_licensor_manager"),
        'licensed_product_ids': fields.many2many(
            'product.product', 'product_licensor_rel', 'licensor_id',
            'product_id', 'Licensed Products',
            groups="product_licensor.group_licensor_manager"),
        'field_percentage': fields.integer(
            'Field Percentage (%)',
            groups="product_licensor.group_licensor_manager",
            help=_('Percentage of the sales to pay to licensor'))
    }
    _defaults = {
        'is_licensor': False,
    }
