# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from .. import excel_importer
import openerp

import xlrd
import logging
_logger = logging.getLogger(__name__)

@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class ImportExcelPrepareValueTestCase(TransactionCase):
    def setUp(self):
        super(TransactionCase, self).setUp()
        self.file_path = 'incoming_shipment.xlsx'
        # file 1
        self.picking_importer = excel_importer.incoming_shipment_excel_importer(
            file_path = 'incoming_shipment.xlsx')
        # file 2
        self.picking_importer2 = excel_importer.incoming_shipment_excel_importer(
            file_path = 'incoming_shipment2.xlsx')

    def tearDown(self):
        super(TransactionCase, self).tearDown()


    def fake_excel_data(self):
        data = []
        ilist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        jlist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        for i in ilist:
            data.append(jlist)
        return data

    def test01_import_data_from_excel(self):        
        data = self.picking_importer.get_excel_data()

        self.assertEqual(1.0, data[0][3])
        self.assertEqual(1.0, data[3][3])
        self.assertEqual(10.0, data[12][3])
        self.assertEqual('33-021', data[1][2])
        self.assertEqual('33-021', data[3][2])
        self.assertEqual('48-055', data[12][2])
        self.assertEqual(u'01-22321', data[0][5])
        self.assertEqual('01-22323', data[2][5])
        self.assertEqual('01-22324', data[3][5])
        self.assertEqual(u'8G-001', data[12][5])

    def test01_import_data_from_excel2(self):        
        data = self.picking_importer2.get_excel_data()

        self.assertEqual(1.0, data[0][3])
        self.assertEqual(20.0, data[2][3])
        self.assertEqual(10.0, data[4][3])
        self.assertEqual('55', data[0][2])
        self.assertEqual('55-0102-19', data[2][2])
        self.assertEqual('55-204', data[4][2])
        self.assertEqual(u'101-22321', data[0][5])
        self.assertEqual('101-22323', data[2][5])
        self.assertEqual('101-22325', data[4][5])

    def test02_prepare_value_after_convert(self):
        val = self.picking_importer.prepare_value()

        # error need conver code
        self.assertEqual(u'东方电子器材厂', val['partner_id'])
        self.assertEqual(1.0, val['move_lines'][0][2]['product_uom_qty'])
        self.assertEqual(10.0, val['move_lines'][12][2]['product_uom_qty'])
        self.assertEqual('33-021', val['move_lines'][1][2]['product_id'])
        self.assertEqual('33-021', val['move_lines'][3][2]['product_id'])
        self.assertEqual('48-055', val['move_lines'][12][2]['product_id'])
        self.assertEqual(u'01-22321', val['move_lines'][0][2]['supplier_seiral_no'])
        self.assertEqual('01-22323', val['move_lines'][2][2]['supplier_seiral_no'])
        self.assertEqual('01-22324', val['move_lines'][3][2]['supplier_seiral_no'])
        self.assertEqual(u'8G-001', val['move_lines'][12][2]['supplier_seiral_no'])

    def test02_prepare_value_from_file2_after_convert(self):
        val = self.picking_importer2.prepare_value()

        # error need conver code
        self.assertEqual(u'寰享科技', val['partner_id'])
        self.assertEqual(40.0, val['move_lines'][1][2]['product_uom_qty'])
        self.assertEqual(10.0, val['move_lines'][3][2]['product_uom_qty'])
        self.assertEqual(1.0, val['move_lines'][5][2]['product_uom_qty'])
        self.assertEqual('GB/T65-2001', val['move_lines'][1][2]['product_id'])
        self.assertEqual('55-205', val['move_lines'][3][2]['product_id'])
        self.assertEqual('55-204', val['move_lines'][4][2]['product_id'])
        self.assertEqual('XX-1154', val['move_lines'][5][2]['product_id'])
        self.assertEqual(u'201-22322', val['move_lines'][1][2]['supplier_seiral_no'])
        self.assertEqual('201-22324', val['move_lines'][3][2]['supplier_seiral_no'])
        self.assertEqual('101-22325', val['move_lines'][4][2]['supplier_seiral_no'])
        self.assertEqual('201-22326', val['move_lines'][5][2]['supplier_seiral_no'])


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class CreatePickingFromImportExcelTestCase(TransactionCase):
    def test_01_prepare_odoo_value_from_excel_value(self):
        picking_importer = excel_importer.incoming_shipment_excel_importer(
            file_path = 'incoming_shipment2.xlsx')
        val = picking_importer.get_value()
        val = self.env['incoming.shipment.converter'].convert_odoo_value_from_value(val)


        # partner
        self.assertEqual(6, val['partner_id'])
        # picking_type_id
        self.assertEqual(1, val['picking_type_id'])
        # qty
        self.assertEqual(40.0, val['move_lines'][1][2]['product_uom_qty'])
        self.assertEqual(10.0, val['move_lines'][3][2]['product_uom_qty'])
        self.assertEqual(1.0, val['move_lines'][5][2]['product_uom_qty'])
        # product_id
        self.assertEqual(20, val['move_lines'][1][2]['product_id'])
        self.assertEqual(12, val['move_lines'][3][2]['product_id'])
        self.assertEqual(13, val['move_lines'][4][2]['product_id'])
        self.assertEqual(14, val['move_lines'][5][2]['product_id'])
        # supplier_serial_no
        self.assertEqual(u'201-22322', val['move_lines'][1][2]['supplier_seiral_no'])
        self.assertEqual('201-22324', val['move_lines'][3][2]['supplier_seiral_no'])
        self.assertEqual('101-22325', val['move_lines'][4][2]['supplier_seiral_no'])
        self.assertEqual('201-22326', val['move_lines'][5][2]['supplier_seiral_no'])
        # uom_id
        self.assertEqual(1, val['move_lines'][5][2]['product_uom'])

        return

    def test02_create_picking_from_excel(self):
        picking_importer = excel_importer.incoming_shipment_excel_importer(
            file_path='incoming_shipment.xlsx')

        excel_val = picking_importer.get_value()
        # fake value to delete
        # val = self.get_fake_value_for_test2()
        odoo_val = self.env['incoming.shipment.converter'].convert_odoo_value_from_value(excel_val)
        picking_ids = self.env['stock.picking'].create(odoo_val)
        self.assertEqual(1, len(picking_ids))

        _logger.warn("\n\n LY test_create_pikcing_from_excel \n\n")
    
    # LY fake value function to delete
    def get_fake_value_for_test2(self):
        val = {
            'partner_id': 1,
            'picking_type_id': 1,
            'move_lines': [
                (0,0,{
                'product_id':4, 'product_uom_qty':5, 'product_uom': 1,
                'location_id':8, 'location_dest_id': 12,
                'name': 'import fake 1',
                }),
                (0,0,{'product_id':3, 'product_uom_qty':3, 'product_uom': 1,
                'location_id':8, 'location_dest_id': 12,
                'name': 'import fake 2',
                })],
        }
        return val

    def test03_create_picking_from_file_path(self):
        file_path = 'incoming_shipment.xlsx'
        picking_ids = self.env[
            'incoming.shipment.converter'].create_picking_from_excel_file_path(
                'incoming_shipment.xlsx')
        self.assertEqual(1, len(picking_ids))

        # self.assertEqual(6, picking_ids[0].partner_id)
        return

    def test04_create_picking_from_file_path(self):
        file_path = 'incoming_shipment.xlsx'
        picking_ids = self.env[
            'incoming.shipment.converter'].create_picking_from_excel_file_path(
                'incoming_shipment.xlsx')
        self.assertEqual(1, len(picking_ids))

        packs = picking_ids[0].pack_operation_ids
        
        # product_id
        self.assertEqual(18, packs[1].product_id.id)
        self.assertEqual(8, packs[12].product_id.id)
        # lot_id, supplier_serial_no
        self.assertEqual('01-22322', packs[1].lot_id.supplier_seiral_no)
        self.assertEqual('8G-001', packs[12].lot_id.supplier_seiral_no)

        inchoming_type_id = self.env.ref('stock.picking_type_in')
        # location_from, supplier_serial_no
        self.assertEqual(
            inchoming_type_id.default_location_src_id.id, packs[1].location_id.id)
        self.assertEqual(
            inchoming_type_id.default_location_dest_id.id, packs[12].location_dest_id.id)

        return

    # def test05_create_picking_from_file_path(self):
    #     file_path = 'incoming_shipment2.xlsx'
    #     picking_ids = self.env[
    #         'incoming.shipment.converter'].create_picking_from_excel_file_path(
    #             'incoming_shipment2.xlsx')
    #     self.assertEqual(1, len(picking_ids))

    #     packs = picking_ids[0].pack_operation_ids
        
    #     # product_id
    #     self.assertEqual(20, packs[1].product_id.id)
    #     self.assertEqual(12, packs[3].product_id.id)
    #     self.assertEqual(13, packs[4].product_id.id)
    #     self.assertEqual(14, packs[5].product_id.id)
    #     # lot_id, supplier_serial_no
    #     self.assertEqual(u'201-22322', packs[1].lot_id.ref)
    #     self.assertEqual('201-22324', packs[3].lot_id.ref)
    #     self.assertEqual('101-22325', packs[4].lot_id.ref)
    #     self.assertEqual('201-22326', packs[5].lot_id.ref)

    #     return