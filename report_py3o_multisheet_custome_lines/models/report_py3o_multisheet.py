# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models

import math
import logging

_logger = logging.getLogger(__name__)


class ReportPy3oMultisheet(models.Model):
    _inherit = 'report.py3o.multisheet'
    _description = 'Report Py3o Multisheet With Custome Lines'

    def multi_attribute_per_line(
            self,
            sheets,
            sheet_lines_data,
            attribute_per_line,
            attribute_num_per_line,
    ):
        """This function would insert multi-attribute into lines per sheets.
        attribute_per_line: attribute list each lines
        attribute_num_per_line: the number of attributes each lines
        sheet_lines_data:
        {
        'Sheet name':{
                    'name': 'Sheet name',
                    'lines': 'Lines number per sheet',
                    'duplicate': True if need to duplicate head and
                                 foot of base sheet,
                    'head_end_line': The number of the line header
                                     ending
                    },
        }
        """
        lines_per_line = int(math.ceil(
            len(attribute_per_line) / float(attribute_num_per_line)))
        total_lines_num = 0
        for index_sheet, sheet in enumerate(sheets):
            total_lines_per_sheet = sheet_lines_data[sheet.name]['lines']
            lines_per_sheet = total_lines_per_sheet / lines_per_line
            head_end_line = sheet_lines_data[sheet.name]['head_end_line']
            for row in range(0, total_lines_per_sheet, lines_per_line):
                for index_attribute, attr in enumerate(attribute_per_line):
                    index_row = \
                        total_lines_num + row / lines_per_line
                    if index_attribute < 4 or 5 < index_attribute < 9:
                        sheet[row +
                              head_end_line +
                              index_attribute /
                              attribute_num_per_line, index_attribute %
                              attribute_num_per_line].\
                            set_value((attr % (index_row)))
                    elif index_attribute >= 9:
                        sheet[row +
                              head_end_line +
                              index_attribute /
                              attribute_num_per_line, index_attribute %
                              attribute_num_per_line + 2]. \
                            set_value((attr % (index_row)))
                    elif index_attribute in [4, 5]:
                        sheet[row + head_end_line, index_attribute].set_value(
                            attr
                        )

            total_lines_num += lines_per_sheet
        return sheets
