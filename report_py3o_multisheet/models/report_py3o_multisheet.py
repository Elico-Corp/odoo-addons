# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api

import math
import copy
import logging
import time
import random
import os

_logger = logging.getLogger(__name__)

try:
    import ezodf
except (ImportError, IOError) as err:
    _logger.debug(err)


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    py3o_template_fallback_base = fields.Char(
        size=128,
        help='If the user does not provide a template '
             'this one will be used.'
    )


class ReportPy3oMultisheet(models.Model):
    _name = 'report.py3o.multisheet'
    _description = 'Report Py3o Multisheet'

    def _get_tmp_folder(self):
        tmp_folder_name = '/tmp/template_multisheet/' + \
                          str(int(time.time())) + \
                          str(int(1000 + random.random() * 1000)) + '/'
        return tmp_folder_name

    def _create_tmp_folder(self, tmp_folder_name):
        cmd = 'mkdir -p ' + tmp_folder_name + '/report/'
        os.system(cmd)

    def open_base_template(self, template_base_path):
        """This function open the base template ods file
        """
        return ezodf.opendoc(template_base_path)

    def save_new_template(self, template_new_path, doc):
        """This function generate the new template ods file
        """
        doc.saveas(template_new_path)
        return True

    def multi_sheet_per_template(
            self,
            sheets,
            sheet_lines_data,
    ):
        """This function generate the new template from base one. It
        duplicate the head and footer of first sheet or duplicate with
        the empty sheet with specific sheet name.
        sheets: sheets of template ods
        sheet_lines_data:
        {
        'Sheet name':{
                    'name': 'Sheet name',
                    'lines': 'Lines number per sheet',
                    'duplicate': True if need to duplicate head and
                                 foot of base sheet,
                    'head_end_line': The number of the line header
                                     ending
        }
        """
        sheet = sheets[0]
        sheet_list = [value for key, value in sheet_lines_data.items()]
        sheet_list.sort(key=lambda x: x['sequence'])
        for value in sheet_list:
            sheet_new = copy.deepcopy(
                sheet) if value['duplicate'] \
                else ezodf.Table[value['name']]
            sheet_new.name = value['name']
            sheets.append(sheet_new)
        del sheets[0]
        return sheets

    def multi_lines_per_sheet(self, sheets, sheet_lines_data):
        """This function insert lines into each sheets
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
        for sheet in sheets:
            # Append the new sheet
            lines_per_sheet = \
                sheet_lines_data[sheet.name].get('lines', 1)
            head_end_line = \
                sheet_lines_data[sheet.name].get('head_end_line', 1)
            sheet.insert_rows(index=head_end_line,
                              count=lines_per_sheet)
        return sheets

    def multi_attribute_per_line(
            self,
            sheets,
            sheet_lines_data,
            attribute_per_line,
            attribute_num_per_line,
    ):
        """This function insert multi-attribute into lines per sheets.
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
                    sheet[row +
                          head_end_line +
                          index_attribute /
                          attribute_num_per_line, index_attribute %
                          attribute_num_per_line].set_value((attr %
                                                             (index_row)))
            total_lines_num += lines_per_sheet
        return sheets

    @api.model
    def template_sheet_with_custom_line(
            self,
            head_end_line,
            lines_per_sheet,
            attribute_per_line,
            summary_line,
            template_new_path,
            template_base_path
    ):
        """This function generate the new template from base one.
        It duplicate the header and footer of first sheet into new sheets,
        and make the body could be customized by user."""
        doc = self.open_base_template(template_base_path)
        sheets = doc.sheets
        sheet = sheets[0]
        for index in range(len(lines_per_sheet) - 1):
            sheet_new = copy.deepcopy(sheet)
            sheets.append(sheet_new)
        for index1, sheet in enumerate(sheets):
            sheet.name = lines_per_sheet[index1]['name']
            sheet.insert_rows(index=head_end_line,
                              count=lines_per_sheet[index1]['lines_number'])
            for row in range(lines_per_sheet[index1]['lines_number']):
                for index2, attr in enumerate(attribute_per_line):
                    sheet[row + head_end_line, index2].\
                        set_value(
                        (attr % (index1 * lines_per_sheet[index1 - 1][
                            'lines_number'] + row)))
            sheet.insert_rows(
                index=head_end_line +
                lines_per_sheet[index1]['lines_number'] + 2,
                count=len(lines_per_sheet[index1]['list'])
            )
            for index, line in enumerate(lines_per_sheet[index1]['list']):
                sheet[head_end_line + lines_per_sheet[index1][
                    'lines_number'] + 2 + index, 0].set_value(line)
        self.save_new_template(template_new_path, doc)
