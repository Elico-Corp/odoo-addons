# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import xlwt
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
import logging
from openerp import SUPERUSER_ID
from openerp.tools.translate import translate
from openerp import _
import datetime
import jdatetime
import tempfile


_logger = logging.getLogger(__name__)

_ir_translation_name = 'report.sale.order.bom.report.xls'
HEIGHT = 300 * 2


class ReportSaleOrderBomParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportSaleOrderBomParser, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime.datetime,
        })


class ReportSaleOrderBom(report_xls):

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, '', 'code', lang, src) or src

    # write table head
    def table_head(self, ws, obj, style0, style1):
        """
            generate fixed table head,return title_list and col number
        """
        ws.row(0).height = 255 * 3
        ws.write_merge(0, 0, 0, 8, u'协邦铸业生产任务单دولت MO ریخته گری در', style0)
        ws.write(1, 0, u'客户名称:\nنام مشتری:', style1)
        partner = obj.partner_id
        if partner and partner.name:
            ws.write(1, 1, partner.name, style1)
        else:
            ws.write(1, 1, '', style1)
        user = obj.user_id
        if user and user.name:
            ws.write_merge(1, 1, 7, 8, user.name, style1)
            ws.write_merge(2, 2, 7, 8, user.name, style1)
        else:
            ws.write_merge(1, 1, 7, 8, u'', style1)
            ws.write_merge(2, 2, 7, 8, u'', style1)
        date_order = datetime.datetime.strptime(obj.date_order,
                                                "%Y-%m-%d %H:%M:%S")
        delivery_date = date_order + datetime.timedelta(days=obj.order_line[0].delay)
        ir_delivery_date = jdatetime.date.fromgregorian(day=delivery_date.day,
                                                        month=delivery_date.month,
                                                        year=delivery_date.year)
        delivery_date_list = [delivery_date.strftime("%Y-%m-%d"),
                              ir_delivery_date.strftime('%Y-%m-%d')]
        ws.write_merge(2, 2, 3, 4, ' '.join(delivery_date_list), style1)
        ws.write(1, 2, u'生产任务单号:\nتعداد MO:', style1)
        ws.write_merge(1, 1, 3, 4, obj.name, style1)
        ws.write_merge(1, 1, 5, 6, u'跟单员:\nMerchandiser:', style1)
        ws.write(2, 0, u'下单日期:\nتنها عضویت:', style1)
        ir_date_order = jdatetime.date.fromgregorian(day=date_order.day,
                                                     month=date_order.month,
                                                     year=date_order.year)
        oder_date = obj.date_order.split(' ')
        date_list = [oder_date[0], ir_date_order.strftime('%Y-%m-%d')]
        ws.write(2, 1, ' '.join(date_list), style1)
        ws.write(2, 2, u'出货日期:\nتاریخ ارسال:', style1)
        ws.write_merge(2, 2, 5, 6, u'业务员:\nفروشنده:', style1)
        # expand col width
        ws.col(1).width = 333 * 18
        ws.col(2).width = 333 * 10
        ws.col(3).width = 333 * 10
        ws.row(0).height = HEIGHT
        ws.row(1).height = HEIGHT
        ws.row(2).height = HEIGHT
        ws.row(3).height = HEIGHT
        ws.row(4).height = HEIGHT
        ws.row(5).height = HEIGHT
        ws.row(6).height = HEIGHT

    def product_title(self, ws, num, style1):
        """
            according to attribute, dynamic print product title.
        """
        ws.write(num, 0, u'产品编码\nکد محصول', style1)
        ws.write_merge(num, num, 1, 2, u'产品名称\nنام محصول', style1)
        ws.write(num, 3, u'数量مقدار', style1)
        ws.write(num, 4, u'装箱率نرخ بسته بندی', style1)
        ws.write_merge(num, num, 5, 8, u'图片تصویر', style1)
        num += 1
        return num

    def product_info(self, ws, num, res, product, style1):
        ws.write(num, 0, res['code'], style1)
        ws.write_merge(num, num, 1, 2, res['name'], style1)
        ws.write(num, 3, res['qty'], style1)
        ws.write(num, 4, res['pack_rate'], style1)
        if product.image_small:
            file_path = tempfile.gettempdir() + '/logo'
            f = open(file_path, 'wb')
            f.write(product.image.decode('base64'))
            f.close()
            ws.write_merge(num, num, 5, 8, '', style1)
            ws.insert_bitmap(file_path, num, 7)
        else:
            ws.write_merge(num, num, 5, 8, '', style1)
        ws.row(num).height = HEIGHT
        num += 1
        return num

    def table_foot(self, ws, num, col, obj, style1):
        """
            generate table foot,return row number
        """
        ws.write(num, 0, u'金工\nرش فلز', style1)
        ws.write_merge(num, num, 1, col, u'', style1)
        ws.row(num).height = HEIGHT
        num += 1
        ws.write(num, 0, u'包装明细\nجزئیات بسته بندی', style1)
        ws.write_merge(num, num, 1, col, u'', style1)
        ws.row(num).height = HEIGHT
        num += 1
        ws.write(num, 0, u'压铸商标\nعلامت تجاری ریخته گری', style1)
        ws.write_merge(num, num, 1, col, u'', style1)
        ws.row(num).height = HEIGHT
        num += 1
        ws.write(num, 0, u'备注\nاظهار', style1)
        if obj.client_order_ref:
            ws.write_merge(num, num, 1, col, obj.client_order_ref, style1)
        else:
            ws.write_merge(num, num, 1, col, u'', style1)
        ws.row(num).height = HEIGHT
        num += 1
        return num

    def bom_head(self, ws, num, style1, style4):
        title_list = []
        ws.write(num, 0, u'材料编码\nکد مواد', style4)
        ws.write(num, 1, u'材料名称\nنام ماده', style1)
        ws.write(num, 2, u'底部پایین', style1)
        ws.write(num, 3, u'内涂توو', style1)
        ws.write(num, 4, u'外涂پوشش داده شده', style1)
        ws.write(num, 5, u'烤温درجه حرارت پخت', style1)
        ws.write(num, 6, u'生产任务单号\nتعداد MO:', style1)
        ws.write(num, 7, u'需用数量\nتعداد مورد نیاز', style1)
        ws.write(num, 8, u'产品名称\nنام محصول', style1)
        ws.row(num).height = HEIGHT
        num += 1
        return num, title_list

    # write table information
    def bom_info(self, ws, num, result, style1):
        """
            generate table information,return row number
        """
        for res in result:
            ws.write(num, 0, res['code'], style1)
            ws.write(num, 1, res['material_name'], style1)
            if res.get('bottom'):
                ws.write(num, 2, res['bottom'], style1)
            else:
                ws.write(num, 2, '', style1)
            if res.get('inner'):
                ws.write(num, 3, res['inner'], style1)
            else:
                ws.write(num, 3, '', style1)
            if res.get('outside'):
                ws.write(num, 4, res['outside'], style1)
            else:
                ws.write(num, 4, '', style1)
            if res.get('bake'):
                ws.write(num, 5, res['bake'], style1)
            else:
                ws.write(num, 5, '', style1)
            ws.write(num, 6, res['sale_no'], style1)
            ws.write(num, 7, res['qty'], style1)
            ws.write(num, 8, res['name'], style1)
            ws.row(num).height = HEIGHT
            ws.col(8).width = 333 * 18
            num += 1
        return num

    def xls_format(self):
        '''
        return xls style
        @return style0, style1, style2, style3
        '''
        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        borders.bottom_colour = 0x3A

        font0 = xlwt.Font()
        font0.name = 'Arial'
        font0.height = 350
        font0.bold = True
        font0.underline = True

        font1 = xlwt.Font()
        font1.name = 'Arial'
        font1.height = 200

        # center
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER

        # left
        alignment1 = xlwt.Alignment()
        alignment1.horz = xlwt.Alignment.HORZ_CENTER
        alignment1.horz = xlwt.Alignment.HORZ_LEFT
        alignment1.vert = xlwt.Alignment.VERT_CENTER

        alignment_just = xlwt.Alignment()
        alignment_just.vert = xlwt.Alignment.VERT_JUSTIFIED
        alignment_just.horz = xlwt.Alignment.HORZ_JUSTIFIED

        # for title
        style0 = xlwt.XFStyle()
        style0.font = font0
        style0.alignment = alignment

        style1 = xlwt.XFStyle()
        style1.font = font1
        style1.borders = borders
        style1.alignment = alignment

        style2 = xlwt.XFStyle()
        style2.font = font1
        style2.alignment = alignment

        style3 = xlwt.XFStyle()
        style3.font = font1
        style3.borders = borders
        style3.alignment = alignment1

        style4 = xlwt.XFStyle()
        style4.font = font1
        style4.borders = borders
        style4.alignment = alignment_just
        return style0, style1, style2, style3, style4

    def get_code(self, product):
        """
            return product default code.
        """
        return product.default_code if product.default_code else ''

    def get_quantity(self, bom_qty, mo_qty, res_qty):
        if mo_qty:
            return (bom_qty / mo_qty) * res_qty
        else:
            return 0.0

    def get_pack_rate(self, product):
        """
            according to product attributes, if has attribute then return
            the first attribute value, else return ''
        """
        return product and product.attribute_value_ids and product.attribute_value_ids[0].name or ''

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        """
            generate hr payslip report
        """
        style0, style1, style2, style3, style4 = self.xls_format()
        for number, obj in enumerate(objects):
            sheet_name = 'Sheet' + str(number + 1)
            ws = wb.add_sheet(sheet_name)
            self.table_head(ws, obj, style0, style1)
            num = 3
            bom_result = []
            mrp_bom = self.pool['mrp.bom']
            num = self.product_title(ws, num, style1)
            flag = False
            for line in obj.order_line:
                obj_dict = {}
                product = line.product_id
                obj_dict['code'] = product.default_code
                obj_dict['name'] = product.name
                obj_dict['qty'] = line.product_uom_qty
                obj_dict['pack_rate'] = self.get_pack_rate(product)
                bom = {}
                pro_bom_ids = mrp_bom.search(self.cr, SUPERUSER_ID,
                                             [('product_tmpl_id', '=',
                                               product.product_tmpl_id.id)],
                                             context=self.context)
                bom['qty'] = line.product_uom_qty
                if pro_bom_ids:
                    bom['mo_ids'] = pro_bom_ids[0]
                    bom_result.append(bom)
                    flag = True
                num = self.product_info(ws, num, obj_dict, product, style1)
            num = self.table_foot(ws, num, 8, obj, style1)
            material = u'领用材料明细\nجزئیات مواد مصادره'
            if flag:
                ws.write_merge(num, num, 0, 8,
                               material, style4)
                ws.row(num).height = 300 * 3
                num += 1
            for res in bom_result:
                mo_objs = mrp_bom.browse(self.cr, SUPERUSER_ID, res['mo_ids'],
                                         self.context)
                for mo in mo_objs:
                    result = []
                    for bom_line in mo.bom_line_ids:
                        obj_dict = {}
                        obj_dict['name'] = mo.product_tmpl_id.name
                        obj_dict['qty'] = self.get_quantity(bom_line.product_qty,
                                                            mo.product_qty,
                                                            res['qty'])
                        bom_product = bom_line.product_id
                        obj_dict['code'] = self.get_code(bom_product)
                        obj_dict['material_name'] = bom_product.name
                        obj_dict['sale_no'] = obj.name
                        for attribute in bom_product.attribute_value_ids:
                            attr = attribute.attribute_id
                            if attr and attr.name and attribute.name:
                                if attr.name == u'底部پایین':
                                    obj_dict['bottom'] = attribute.name
                                elif attr.name == u'内涂توو':
                                    obj_dict['inner'] = attribute.name
                                elif attr.name == u'外涂پوشش داده شده':
                                    obj_dict['outside'] = attribute.name
                                elif attr.name == u'烤温درجه حرارت پخت':
                                    obj_dict['bake'] = attribute.name
                        result.append(obj_dict)
                    num, title_list = self.bom_head(ws, num, style1, style4)
                    num = self.bom_info(ws, num, result, style1)


ReportSaleOrderBom(
    'report.report.sale.order.bom.report.xls', 'sale.order',
    parser=ReportSaleOrderBomParser)
