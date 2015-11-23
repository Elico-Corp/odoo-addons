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
_logger = logging.getLogger(__name__)


class import_product_from_excel_wizard(osv.osv_memory):
    _name = 'import.product.from.excel.wizard'
    _descript = 'Import Product From Excel Wizard'
    _file_path = "/tmp/1_odoo_product_from_excel.xls"

    _columns = {
        'excel': fields.binary("产品"),
    }

    def import_product_from_excel(self, cr, uid, ids, context=None):
        # save file on server
        sysstr = platform.system()
        if(sysstr == "Windows"):
            self._file_path = "c:/1_odoo_product_from_excel.xls"
        
        self.save_excel(cr, uid, ids, context)
        self.pool.get('product.converter').create_product_from_excel_file_path(cr, uid, file_path=self._file_path)

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


class ProductConverter(osv.osv):
    _name = 'product.converter'

    @api.model
    def create_product_from_excel_file_path(self, file_path):
        product_importer = product_excel_importer(file_path=file_path)
        excel_val = product_importer.get_value()

        product_ids=[]
        product_create_list = self.convert_odoo_value_from_value(excel_val)
        for product_vals in product_create_list:
            product_id = self.env['product.template'].create(product_vals)
            product_ids.append(product_id)
        return product_ids

    @api.model
    def convert_odoo_value_from_value(self, excel_val):
        self.original_excel_val = excel_val or []
        
        product_create_list = []
        for product in excel_val:
            if not product['default_code']:
                raise osv.except_osv(u'错误',u'[%s]的产品定义码必须输入!'%product['name'])
            if not product['uom_type']:
                raise osv.except_osv(u'错误',u'[%s]的单位类型必须输入!'%product['name'])

            if not self.find_product_id_from_sku(product['default_code']):
                product_type = product['type'].encode('utf8')
                #LY 0601 for
                product['sale_ok'] = False
                if product_type in ['消耗品','consu']:
                    product['type'] = "consu"
                elif product_type in ['服务','service']:
                    product['type'] = "service"
                #LY 0601
                elif product_type in ['产成品', 'product']:
                    product['type'] = 'product'
                    product['sale_ok'] = True
                #LY 0601 END
                else:
                    product['type'] = "product"

                uom_type = product['uom_type'].encode('utf8')
                if uom_type == '个':
                    product['uom_type'] = "one"
                elif uom_type == '批':
                    product['uom_type'] = "multi"
                else:
                    raise osv.except_osv(u'错误',u'[%s]的单位类型必须为个或批!'%product['name'])

                supply_method = product['supply_method'].encode('utf8')
                if supply_method == '生产':
                    product['supply_method'] = "manufacture"
                elif supply_method == '购买':
                    product['supply_method'] = "purchase"
                else:
                    raise osv.except_osv(u'错误',u'[%s]的单位类型必须为生产或购买!'%product['supply_method'])

                product_create_list.append(product)
            else:
                raise osv.except_osv(u'错误',u'[%s]的产品定义码重复!'%product['name'])

        return product_create_list

    @api.model
    def find_product_id_from_sku(self, product_sku):
        product = self.env['product.product'].search([('default_code', '=', product_sku)], limit=1)
        if not product.id:
            return False

        return True

class product_excel_importer(excel_importer.excel_importer):
    def __init__(self, file_path=None, excel_bin_value=None):
        super(product_excel_importer, self).__init__(
            file_path=file_path, excel_bin_value=excel_bin_value)

    def _prepare_product_data(self):
        lines = []
        for row in self.excel_data:
            line = {
                'name': row[0].strip(),
                'default_code': str(row[1]).strip(),# to convert float into str to use strip
                'supply_method': row[2].strip(),
                'type': row[3].strip(),
                #'uom_description':row[2].strip(),
                'uom_type': row[4].strip(),
                'type_specification': row[5].strip(),
                'figure_number': row[6].strip(),
                'remark': row[7].strip(),
                'product_description': row[8].strip(),
                'project_code': row[9].strip(),
                'quality_grade': row[10].strip(),
                'standard_number': row[11].strip(),
                #'categ_id':osv.osv.env.ref('product.product_category_all'),
                #'uom_id':osv.osv.env.ref('product.product_uom_unit'),
            }
            lines.append(line)

        self.value = lines
        return

    def prepare_value(self):
        self._prepare_product_data()
        return self.value