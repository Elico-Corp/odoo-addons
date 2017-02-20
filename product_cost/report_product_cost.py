# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import xlwt
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
import logging
from openerp.tools.translate import translate

_logger = logging.getLogger(__name__)

_ir_translation_name = 'report.product.cost.batch.report.xls'


class ReportProductCostParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportProductCostParser, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
        })


class ReportProductCost(report_xls):

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, '', 'code', lang, src) or src

    def __init__(self, name, table, rml=False,
                 parser=False, header=True, store=False):
        super(ReportProductCost, self).__init__(
            name, table, rml, parser, header, store)

    # write table head
    def table_head(self, ws, obj, style0, style1):
        """
            generate fixed table head,return title_list and col number
        """
        ws.row(0).height = 255 * 3
        ws.write_merge(0, 0, 0, 16, obj.name, style0)
        ws.write(1, 0, self._('manufacture task number'), style1)
        ws.write(1, 1, self._('customer'), style1)
        ws.write(1, 2, self._('product code'), style1)
        ws.write(1, 3, self._('product name'), style1)
        ws.write(1, 4, self._('unit'), style1)
        ws.write(1, 5, self._('finished number'), style1)
        ws.write(1, 6, self._('sale income'), style1)
        ws.write(1, 7, self._('material cost'), style1)
        ws.write(1, 8, self._('resource cost'), style1)
        ws.write(1, 9, self._('manufacture cost'), style1)
        ws.write(1, 10, self._('total'), style1)
        ws.write(1, 11, self._('sale profit'), style1)
        ws.write(1, 12, self._('sale profit percent%'), style1)
        ws.write(1, 13, self._('unit material cost'), style1)
        ws.write(1, 14, self._('unit resource cost'), style1)
        ws.write(1, 15, self._('unit manufacture fee'), style1)
        ws.write(1, 16, self._('unit cost'), style1)
        # expand col width
        ws.col(1).width = 333 * 22

    # write table information
    def table_info(self, ws, num, result, style1):
        """
            generate table information,return row number
        """
        for res in result:
            ws.write(num, 0, res['mo_id'], style1)
            ws.write(num, 1, res['customer_id'], style1)
            ws.write(num, 2, res['product_code'], style1)
            ws.write(num, 3, res['product_name'], style1)
            ws.write(num, 4, res['uom'], style1)
            ws.write(num, 5, res['finished_product_number'], style1)
            ws.write(num, 6, res['sale_income'], style1)
            ws.write(num, 7, res['material_cost'], style1)
            ws.write(num, 8, res['resource_cost'], style1)
            ws.write(num, 9, res['manufacture_cost'], style1)
            ws.write(num, 10, res['total'], style1)
            ws.write(num, 11, res['sale_profit'], style1)
            ws.write(num, 12, res['sale_profit_percent'], style1)
            ws.write(num, 13, res['unit_material_cost'], style1)
            ws.write(num, 14, res['unit_resource_cost'], style1)
            ws.write(num, 15, res['unit_manufacture_cost'], style1)
            ws.write(num, 16, res['unit_cost'], style1)
            num += 1
        return num

    def xls_format(self):
        '''
        return xls style
        @return style0, style1
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

        # for title
        style0 = xlwt.XFStyle()
        style0.font = font0
        style0.alignment = alignment

        style1 = xlwt.XFStyle()
        style1.font = font1
        style1.borders = borders
        style1.alignment = alignment

        return style0, style1

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        """
            generate hr payslip report
        """
        style0, style1 = self.xls_format()
        ws = wb.add_sheet('Sheet1')
        self.table_head(ws, objects, style0, style1)
        num = 2
        result = []
        for product_cost in objects.cost_ids:
            obj_dict = {}
            obj_dict['mo_id'] = product_cost.mo_id.name
            obj_dict['customer_id'] = \
                product_cost.customer_id.name if product_cost.customer_id \
                else ''
            obj_dict['product_name'] = product_cost.product_name.name
            obj_dict['product_code'] = \
                product_cost.product_code if product_cost.product_code else ''
            obj_dict['uom'] = product_cost.uom.name
            obj_dict['finished_product_number'] = \
                product_cost.finished_product_number
            obj_dict['sale_income'] = product_cost.sale_income
            obj_dict['material_cost'] = product_cost.material_cost
            obj_dict['resource_cost'] = product_cost.resource_cost
            obj_dict['manufacture_cost'] = product_cost.manufacture_cost
            obj_dict['total'] = product_cost.total
            obj_dict['sale_profit'] = product_cost.sale_profit
            obj_dict['sale_profit_percent'] = product_cost.sale_profit_percent
            obj_dict['unit_material_cost'] = product_cost.unit_material_cost
            obj_dict['unit_resource_cost'] = product_cost.unit_resource_cost
            obj_dict['unit_manufacture_cost'] = \
                product_cost.unit_manufacture_cost
            obj_dict['unit_cost'] = product_cost.unit_cost
            result.append(obj_dict)
        num = self.table_info(ws, num, result, style1)


ReportProductCost(
    'report.report.product.cost.batch.report.xls', 'product.cost.batch',
    parser=ReportProductCostParser)
