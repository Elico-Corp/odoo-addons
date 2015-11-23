# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from  openerp.osv import osv, fields
from openerp.tools.translate import _
from .. import excel_importer
from openerp import api,_
import base64
import platform
import logging
import datetime
_logger = logging.getLogger(__name__)


class import_picking_from_excel_wizard(osv.osv_memory):
    '''
    Mass Email to  Supplier Customer
    '''
    _name = 'import.picking.from.excel.wizard'
    _descript = 'Import Picking From Excel Wizard'
    _file_path = "/tmp/1_odoo_picking_from_excel.xls"

    _columns = {
        'excel': fields.binary("原料入库单"),
    }

    def import_picking_from_excel(self, cr, uid, ids, context=None):

        sysstr = platform.system()
        if(sysstr =="Windows"):
            self._file_path = "c:/1_odoo_picking_from_excel.xls"

        # save file on server
        self.save_excel(cr, uid, ids, context)

        #todo move into incoming.shipment.converter
        #try:
        picking_ids = self.pool.get('incoming.shipment.converter').create_picking_from_excel_file_path(cr, uid, file_path=self._file_path)
        #except:
            #import traceback
            #@_logger.error(traceback.format_exc())
            #_logger.warn("\n\n  Error Import in wizard ! \n\n")
        #    raise Warning(u"错误",u"导入失败，请检查导入文件.")

        #todo  add exception warning LY

        return {'type': 'ir.actions.act_window_close'}

    def save_excel(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)[0]
        if not data.excel:
            raise osv.except_osv(u'错误',u'请选择要导入的Excel文件!')

        file_path = self._file_path
        f = open(file_path, 'wb')
        uploaded_file = base64.decodestring(data.excel)
        f.write(uploaded_file)
        f.close()
        return {'type': 'ir.actions.act_window_close'}

class incomingShipmentConverter(osv.osv):
    _name = 'incoming.shipment.converter'

    @api.model
    def create_picking_from_excel_file_path(self, file_path):
        picking_importer = incoming_shipment_excel_importer(file_path=file_path)
        excel_val = picking_importer.get_value()

        updated_ship_val = self.convert_odoo_value_from_value(excel_val)
        picking_ids = self.env['stock.picking'].create(updated_ship_val)
        return picking_ids

    @api.model
    def convert_odoo_value_from_value(self, excel_val):
        self.original_excel_val = excel_val or []
        ship_val_after_header_update = self.update_shipping_header(excel_val)
        ship_val_after_lines_update = self.update_shipping_move_lines(ship_val_after_header_update)
        #updated_ship_val = self.update_shipping_pack_operations(ship_val_after_lines_update)
        return ship_val_after_lines_update

    @api.model
    def update_shipping_header(self, excel_val):
        ship_val_after_header_update = excel_val
        ship_val_after_header_update['picking_type_id'] = self.get_picking_type_id()
        ship_val_after_header_update['partner_id'] = self.find_create_partner_id(excel_val['partner_id'])

        return ship_val_after_header_update

    @api.model
    def update_shipping_move_lines(self, ship_val_after_header_update):
        ship_val_after_lines_update = ship_val_after_header_update
        excel_move_lines = ship_val_after_header_update['move_lines']
        
        updated_move_lines = []
        for excel_line in excel_move_lines:
            updated_move_lines.append(self.update_one_move_line(excel_line))#根据产品名称，单位名称更新产品ID,单位ID
        ship_val_after_lines_update['move_lines'] = updated_move_lines

        return ship_val_after_lines_update

    @api.model
    def update_one_move_line(self, excel_line):
        updated_line = excel_line
            
        updated_line[2]['product_id']=self.find_create_product_id_from_sku(excel_line[2]['product_id'],excel_line[2]['product_name'])
        updated_line[2]['product_uom']=self.find_create_uom_from_name(excel_line[2]['product_uom'])
        updated_line[2]['location_id']=self.find_location_src_dest_from_picking_type()[0]
        updated_line[2]['location_dest_id']=self.find_location_src_dest_from_picking_type()[1]
        #***add by xie xiaopeng***#
        updated_line[2]['restrict_lot_id']= self.create_find_serial_number(updated_line)
        #***end add by xie xiaopeng***#

        #LY post fix after
        updated_line = self.remove_unused_move_data(updated_line)
        return updated_line

    @api.model
    def remove_unused_move_data(self, move_line):
        #pop 'validati_from'
        move_line[2].pop('vlidity_from')
        move_line[2].pop('vlidity_to')
        return move_line

    @api.model
    def update_shipping_pack_operations(self, ship_val_after_lines_update):
        updated_ship_val = ship_val_after_lines_update
        pack_opera_vals = []
        for move in ship_val_after_lines_update['move_lines']:
            pack_line = self.update_one_pack_line(move)
            pack_opera_vals.append(pack_line)
        updated_ship_val['pack_operation_ids'] = pack_opera_vals
        return updated_ship_val

    @api.model
    def update_one_pack_line(self, move):
        updated_pack_line = (0,0,{})
        updated_pack_line[2]['product_id'] = move[2]['product_id']
        updated_pack_line[2]['product_uom_id'] = move[2]['product_uom']
        updated_pack_line[2]['product_qty'] = move[2]['product_uom_qty']
        #updated_pack_line[2]['uom_description'] = move[2]['uom_description']
        updated_pack_line[2]['location_id'] = self.find_location_src_dest_from_picking_type()[0]
        updated_pack_line[2]['location_dest_id'] = self.find_location_src_dest_from_picking_type()[1]
        #***add by xie xiaopeng***#
        updated_pack_line[2]['processed']='true'
        #updated_pack_line[2]['supplier_seiral_no'] = move[2]['product_uom']
        #updated_pack_line[2]['lot_id'] = self.create_find_serial_number(move)
        updated_pack_line[2]['lot_id'] = move[2]['restrict_lot_id']
        #***add by xie xiaopeng***#

        return updated_pack_line

    @api.model
    def create_find_serial_number(self, move):
        product_id = move[2]['product_id']
        supplier_seiral_no = move[2]['supplier_seiral_no']
        #add by wlp
        if not move[2]['product_uom_qty']:
            raise osv.except_osv(u'错误:[%s]必须输入数量'%move[2]['name'],'')
        if not move[2]['uom_description']:
            raise osv.except_osv(u'错误:[%s]必须输入数量单位'%move[2]['name'],'')
        if not move[2]['product_name']:
            raise osv.except_osv(u'错误:[%s]必须输入产品名称'%move[2]['name'],'')

        #add by xiexiaopeng
        product_id = move[2]['product_id']
        product = self.env['product.product'].browse(product_id)
        if move[2]['product_uom_qty'] > 1 and product.uom_type == "one":
            raise osv.except_osv(u'错误:[%s]数量类型为[个]时,数量不能大于1,请拆分成每行数量为1.'%move[2]['name'],'')

        default_code = product.default_code
        vlidity_from = move[2]['vlidity_from']
        vlidity_to = move[2]['vlidity_to']
        reinspec_way = move[2]['reinspec_way']
        production_date = move[2]['production_date']
        reinspec_number = move[2]['reinspec_number']
        production_batch = move[2]['production_batch']
        structure_level = move[2]['structure_level']
        usage_mode = move[2]['usage_mode']
        concession_or_replace_number = move[2]['concession_or_replace_number']
        meterial_plan_status = move[2]['meterial_plan_status']
        meterial_quality_status = move[2]['meterial_quality_status']
        quality_info_number = move[2]['quality_info_number']
        special_requirement = move[2]['special_requirement']
        material = move[2]['material']
        design_quality = move[2]['design_quality']
        product_category = move[2]['product_category']
        
        #use ref or supplier_serial_no will affect here,  test, 
        if not supplier_seiral_no:
            product_name = self.env['product.product'].search_read([('id', '=',product_id)],['name'],limit=1)[0]['name']
            raise osv.except_osv(u'错误',u"产品%s没有供应商序列号!"%product_name)

        lot_obj = self.env['stock.production.lot']
        lot_id = lot_obj.search([('supplier_seiral_no', '=', supplier_seiral_no),('product_id.default_code', '=', default_code)], limit=1)
        if not lot_id:
            lot_id = lot_obj.create({
                'product_id': product_id,
                'supplier_seiral_no': supplier_seiral_no,
                #add by wlp
                'vlidity_from': vlidity_from,
                'vlidity_to': vlidity_to,
                'reinspec_way':reinspec_way,
                'production_date':production_date,
                'reinspec_number':reinspec_number,
                'production_batch':production_batch,
                'structure_level':structure_level,
                'usage_mode':usage_mode,
                'concession_or_replace_number':concession_or_replace_number,
                'meterial_plan_status':meterial_plan_status,
                'meterial_quality_status':meterial_quality_status,
                'quality_info_number':quality_info_number,
                'special_requirement':special_requirement,
                'material':material,
                'design_quality':design_quality,
                'product_category':product_category,
            })
        return lot_id.id

    @api.model
    def get_picking_type_id(self):
        # inchoming_type_id
        inchoming_type_id = self.env.ref('stock.picking_type_in')
        return inchoming_type_id.id

    @api.model
    def find_create_partner_id(self, partner_name):
        if not partner_name:
            raise osv.except_osv(u'错误',u'供应商名称不能为空')
        parnter_obj = self.env['res.partner']
        partner_id = parnter_obj.search([('name', '=', partner_name)], limit=1)
        if not partner_id:
            partner_id = parnter_obj.create({'name': partner_name})
        return partner_id.id

    @api.model
    def find_create_product_id_from_sku(self, product_sku,product_name):
        product_id = self.env['product.product'].search([('default_code', '=', product_sku)], limit=1)
        if not product_id.id or product_id.name != product_name:
            # todo option, create product
            raise osv.except_osv(u'错误',u"没有找到产品定义码为%s产品或该定义码的产品名称有误!"%product_sku)

        return product_id.id

    @api.model
    def find_create_uom_from_name(self, original_uom_desc):
        #经过客户确认后，产品单位会统一，只作为规格描述
        uom_id = self.env.ref('product.product_uom_unit')
        return uom_id.id

    @api.model
    def find_location_src_dest_from_picking_type(self):
        inchoming_type_id = self.env.ref('stock.picking_type_in')
        return inchoming_type_id.default_location_src_id.id, inchoming_type_id.default_location_dest_id.id

class incoming_shipment_excel_importer(excel_importer.excel_importer):

    def __init__(self, file_path=None, excel_bin_value=None):
        super(incoming_shipment_excel_importer, self).__init__(
            file_path=file_path, excel_bin_value=excel_bin_value)


    def _prepare_shipment_header(self):
        val = {
            'partner_id': self.excel_data[0][0].strip(),
        }
        self.value = val
        return


    def _prepare_shipment_moves(self):
        lines = []
        for row in self.excel_data:
            line = (0,0, {
                    'product_id':row[2].strip(),
                    'product_uom_qty':row[3],
                    'name': row[2].strip(), 
                    'product_name':row[1].strip(),
                    'supplier_seiral_no': row[5].strip(),
                    'uom_description': row[4].strip(),
                    'vlidity_from':row[7].strip(),
                    'vlidity_to':row[8].strip(),
                    'reinspec_way':row[9].strip(),
                    'production_date':row[10].strip(),
                    'reinspec_number':row[11].strip(),
                    'production_batch':row[12],
                    'structure_level':row[13],
                    'usage_mode':row[14].strip(),
                    'concession_or_replace_number':row[15].strip(),
                    'meterial_plan_status':row[16].strip(),
                    'meterial_quality_status':row[17].strip(),
                    'quality_info_number':row[18].strip(),
                    'special_requirement':row[19].strip(),
                    'product_category': row[20].strip(),
                    'material': row[21].strip(),
                    'design_quality': row[22].strip(),
                    'product_uom': row[4],
                    'location_id':8,
                    'location_dest_id': 12,
                    })
            lines.append(line)
        
        val = {'move_lines': lines};
        self.value.update(val)
        return
    
    #only use for test
    def prepare_value(self):
        self._prepare_shipment_header()
        self._prepare_shipment_moves()
        return self.value

def convert_float_to_date(float_val):
    int_val=int(float_val)
    return datetime.date(1900,1,1)+datetime.timedelta(days=(int_val-2))