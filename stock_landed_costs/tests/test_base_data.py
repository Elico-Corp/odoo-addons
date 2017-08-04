# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.test.common import TransactionCase


class TransactionCaseBaseData(TransactionCase):
    def setUp(self):
        cr, uid = self.cr, self.uid
        # base objects
        self.picking_obj = self.registry('stock.picking')
        self.move_obj = self.registry('stock.move')
        self.location_obj = self.registry('stock.location')
        self.model_data_obj = self.registry('ir.model.data')

        # base data for this module's test

        # locations
        self.duty_free_locaton_id = self.model_data_obj.get_object_reference(
            cr, uid, 'stock_location', 'stock_location_duty_free_zone_001')[1]
        self.duty_paid_location_id = self.model_data_obj.get_object_reference(
            cr, uid, 'stock_location', 'stock_location_duty_paid_zone_001')[1]
        self.transit_location_id = self.model_data_obj.get_object_reference(
            cr, uid, 'stock_location', 'stock_location_transit')[1]

        # company
        self.company_id = self.model_data_obj.get_object_reference(
            cr, uid, 'res.company', 'base.main_company')[1]

        # picking
        self.picking_id = self.picking_obj.create(
            cr, uid, self.prepare_base_picking('direct'))

    def prepare_base_picking(self, type):
        '''prepare the base picking'''
        return {
            'name': 'Picking1',
            'state': 'auto',
            'type': type,
            'move_type': 'direct',
            'invoice_state': 'none',
            'company_id': self.company_id
        }

    def tearDown(self):
        self.cr.rollback()
