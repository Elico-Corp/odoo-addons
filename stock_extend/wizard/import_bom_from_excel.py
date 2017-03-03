# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
import platform

from openerp import api
from openerp.osv import osv, fields

from .. import excel_importer

_logger = logging.getLogger(__name__)


class import_bom_from_excel_wizard(osv.osv_memory):
    _name = 'import.bom.from.excel.wizard'
    _descript = 'Import Bom From Excel Wizard'
    _file_path = "/tmp/1_odoo_bom_from_excel.xls"

    _columns = {
        'excel': fields.binary("物料清单"),
    }

    def import_bom_from_excel(self, cr, uid, ids, context=None):
        sysstr = platform.system()
        if (sysstr == "Windows"):
            self._file_path = "c:/1_odoo_bom_from_excel.xls"

        # save file on server
        self.save_excel(cr, uid, ids, context)
        bom_ids = self.pool.get('bom.converter')\
            .create_bom_from_excel_file_path(
            cr, uid, file_path=self._file_path)

        return {'type': 'ir.actions.act_window_close'}

    def save_excel(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)[0]
        if not data.excel:
            raise osv.except_osv(u'错误', u'请选择要导入的Excel文件!')

        file_path = self._file_path
        f = open(file_path, 'wb')
        uploaded_file = base64.decodestring(data.excel)
        f.write(uploaded_file)
        f.close()
        return {'type': 'ir.actions.act_window_close'}


class BomConverter(osv.osv):
    _name = 'bom.converter'

    @api.model
    def create_bom_from_excel_file_path(self, file_path):
        bom_importer = bom_excel_importer(file_path=file_path)
        excel_val = bom_importer.get_value()
        excel_val = excel_val.values()
        bom_vals = self.convert_odoo_value_from_value(excel_val)
        bom_ids = []
        for val in bom_vals:
            bom_id = self.env['mrp.bom'].create(val)
            bom_ids.append(bom_id)
        return bom_ids

    @api.model
    def convert_odoo_value_from_value(self, excel_val):
        self.original_excel_val = excel_val or []

        bom_update_header = self.update_bom_header(excel_val)
        bom_data = self.update_bom_lines(bom_update_header)
        return bom_data

    @api.model
    def update_bom_header(self, excel_val):
        bom_update_header = excel_val

        for val in bom_update_header:
            product = self.find_create_product_id_from_sku(val['product_id'])

            val['name'] = product['name']
            val['product_tmpl_id'] = product['product_tmpl_id']
            val['product_id'] = product['product_id']

        return bom_update_header

    @api.model
    def find_create_product_id_from_sku(self, product_sku):
        product = self.env['product.product'].search(
            [('default_code', '=', product_sku)], limit=1)
        if not product.id:
            # todo option, create product
            raise osv.except_osv(u'错误', u"没有找到内部编号为[%s]的产品!" % product_sku)

        return {
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'name': product.name
        }

    @api.model
    def update_bom_lines(self, bom_update_header):
        bom_update_lines = bom_update_header
        for line in bom_update_lines:
            excel_bom_lines = line['bom_line_ids']
            updated_bom_lines = []
            for excel_line in excel_bom_lines:
                updated_bom_lines.append(self.update_one_bom_line(excel_line))
                # 根据产品名称，单位名称更新产品ID,单位ID

            line['bom_line_ids'] = updated_bom_lines

        for line in bom_update_lines:
            excel_bom_lines = line['bom_line2_ids']
            updated_bom_lines = []
            for excel_line in excel_bom_lines:
                updated_bom_lines.append(self.update_one_bom_line(excel_line))
                # 根据产品名称，单位名称更新产品ID,单位ID

            line['bom_line2_ids'] = updated_bom_lines

        return bom_update_lines

    @api.model
    def update_one_bom_line(self, excel_line):
        updated_line = excel_line

        product = self.find_create_product_id_from_sku(
            excel_line[2]['product_id'])
        updated_line[2]['product_id'] = product['product_id']

        try:
            product_uos_qty = float(excel_line[2].get('product_uos_qty', 0))
        except:
            raise osv.except_osv(u'错误', u"物料[%s]的数量必须为数字!" % product['name'])

        if product_uos_qty <= 0:
            raise osv.except_osv(u'错误', u"物料[%s]的数量必须大于0!" % product['name'])

        return updated_line


class bom_excel_importer(excel_importer.excel_importer):
    def __init__(self, file_path=None, excel_bin_value=None):
        super(bom_excel_importer, self).__init__(
            file_path=file_path, excel_bin_value=excel_bin_value)

    def _prepare_bom_lines(self):

        product_id_pre = False
        vals = {}
        for row in self.excel_data:

            product_id_cur = row[1].strip()

            if product_id_cur:
                product_id_pre = product_id_cur
            else:
                product_id_cur = product_id_pre

            if row[5] == u'\u4e3b\u6599':
                # u'\u8f85\u6599'    辅料     u'\u4e3b\u6599'  主料
                if product_id_cur and row[3] and row[4]:
                    bom_line = (
                    0, 0,
                    {
                        'product_id': row[3].strip(),
                        'product_uos_qty': row[4],
                        'product_qty': row[4],
                    })
                    if not vals.get(product_id_cur, False):
                        val = {product_id_cur: {
                            'name': row[0],
                            'product_tmpl_id': product_id_cur,
                            'product_id': product_id_cur,
                            'product_qty': 1,
                            'bom_line_ids': [bom_line],
                            'bom_line2_ids': []}
                        }

                        vals.update(val)
                    else:
                        vals[product_id_cur]['bom_line_ids'].append(bom_line)

            elif row[5] == u'\u8f85\u6599':

                if product_id_cur and row[3] and row[4]:
                    bom_line = (
                    0, 0,
                    {
                        'product_id': row[3].strip(),
                        'product_uos_qty': row[4],
                        'product_qty': row[4]
                    })
                    if not vals.get(product_id_cur, False):
                        val = {product_id_cur: {
                            'name': row[0],
                            'product_tmpl_id': product_id_cur,
                            'product_id': product_id_cur,
                            'product_qty': 1,
                            'bom_line_ids': [],
                            'bom_line2_ids': [bom_line]
                        }}

                        vals.update(val)
                    else:
                        vals[product_id_cur]['bom_line2_ids'].append(bom_line)
            else:
                pass

        self.value.update(vals)
        return

    def prepare_value(self):
        self._prepare_bom_lines()
        return self.value
