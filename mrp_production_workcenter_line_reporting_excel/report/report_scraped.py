# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

try:
    import xlwt
except ImportError:
    xlwt = None
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls


class ReportScrapedParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportScrapedParser, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        wanted_list = []
        template_changes = {}
        self.localcontext.update({
            'wanted_list': wanted_list,
            'template_changes': template_changes
        })


class ReportStockScraped(report_xls):
    def __init__(
        self, name, table, rml=False, parser=False, header=True, store=False
    ):
        super(ReportStockScraped, self).__init__(
            name, table, rml, parser, header, store
        )

    def _write_table_row(self, ws, row, start_col, total_col, data, style):
        length = len(data)

        for col in range(start_col, length):
            ws.write(row, col, data[str(col)], style)

        for col in range(length, total_col):
            ws.write(row, col, "", style)

    def _write_table_head(
        self, ws, row, start_col, total_col, main_title, titles, style
    ):
        ws.write_merge(
            1, 1, start_col, total_col - 1, main_title, style)
        self._write_table_row(ws, row + 1, start_col, total_col, titles, style)

    def _write_table_info(self, ws, row, start_col, total_col, lines, style):
        for line in lines:
            self._write_table_row(ws, row, start_col, total_col, line, style)
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

    def _get_table_info(self, titles, records):
        result = []

        for key, res in records.items():
            # save the in the format: col:value
            val = {
                "0": res['name'],
                "1": res['customer'],
                "2": res['product'],
                "3": res['bottom'],
                "4": res['inside'],
                "5": res['outside'],
                "6": res['quantity'],
                "7": res['total_scraped'],
                "8": res['scraped_percentage']
            }
            index = {}
            for col in range(9, len(titles)):
                index[titles[str(col)]] = str(col)
                val[str(col)] = ""

            for process in res['process']:
                scraped_qty = res['scraped_qty'][process] or 0
                val[index[process]] = scraped_qty

            result.append(val)

        return sorted(result, key=lambda rec: (rec['0'], rec['2']))

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        records = data['records']
        # table writer
        ws = wb.add_sheet('Scraped')
        # style
        style = self._get_xls_format()
        # start col index
        col = 0
        total_col = len(data['title'])

        main_title = u"\
        协邦铸业生产工序报废报告انجمن صنعت ریخته گری فرآیندهای تولید دولت قراضه گزارش"
        self._write_table_head(
            ws,
            # start row
            1,
            col,
            total_col,
            main_title,
            # title
            data['title'],
            style
        )

        if records:
            self._write_table_info(
                ws,
                # start row
                3,
                col,
                total_col,
                # table info
                self._get_table_info(data['title'], records),
                style
            )

ReportStockScraped(
    'report.mrp.scraped.xls', 'report.scraped',
    parser=ReportScrapedParser)
