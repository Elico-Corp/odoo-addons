# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

try:
    import xlwt
except ImportError:
    xlwt = None
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls


class ReportStockValuationParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportStockValuationParser, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        wanted_list = []
        template_changes = {}
        self.localcontext.update({
            'wanted_list': wanted_list,
            'template_changes': template_changes
        })


class ReportStockValuationProduction(report_xls):
    def __init__(
        self, name, table, rml=False, parser=False, header=True, store=False
    ):
        super(ReportStockValuationProduction, self).__init__(
            name, table, rml, parser, header, store)

    def _write_table_row(self, ws, row, col, data, style):
        length = len(data)
        for col in range(col, length):
            ws.write(row, col, data[str(col)], style)

    def _write_table_head(self, ws, row, col, main_title, titles, style):
        length = len(titles)
        ws.write_merge(0, 0, 0, length - 1, main_title, style)
        self._write_table_row(ws, row, col, titles, style)

    def _write_table_info(self, ws, row, col, lines, style):
        for line in lines:
            self._write_table_row(ws, row, col, line, style)
            row += 1

    def _get_xls_format(self):
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

        style = xlwt.XFStyle()
        style.font = font1
        style.borders = borders
        style.alignment = alignment

        return style

    def _get_table_info(self, objects):
        result = []

        for line in objects.lines:
            # save the in the format: col:value
            val = {
                "0": line.product_id,
                "1": line.source,
                "2": line.default_code,
                "3": line.cate,
                "4": line.month_inventory,
                "5": line.month_real_cost,
                "6": line.month_inventory_value,
                "7": line.stock_in,
                "8": line.stock_in_real_cost,
                "9": line.stock_in_inventory_value,
                "10": line.stock_out,
                "11": line.stock_out_real_cost,
                "12": line.stock_out_inventory_value,
                "13": line.stock,
                "14": line.stock_real_cost,
                "15": line.stock_inventory_value,
            }

            result.append(val)

        return result

    def _get_main_title(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        location = data['location']
        company = data['company']

        return "%s %s to %s Location: %s \"Stock input/\
            output valuation Report\"" % (
            company, start_date, end_date, location)

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # table writer
        ws = wb.add_sheet('Stock Valutaion')
        # style
        style = self._get_xls_format()
        # col index
        col = 0

        main_title = self._get_main_title(data)

        self._write_table_head(
            ws,
            # start row
            1,
            # start col
            col,
            main_title,
            # title
            data['title'],
            style
        )

        if objects:
            self._write_table_info(
                ws,
                # start row
                2,
                # start col
                col,
                # table info
                self._get_table_info(objects),
                style
            )


ReportStockValuationProduction(
    'report.stock.valuation.report.xls', 'report.stock.list',
    parser=ReportStockValuationParser)
