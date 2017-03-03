# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields

try:
    import xlrd
except ImportError, e:
    pass

import logging

_logger = logging.getLogger(__name__)


# TODO: refactoring csv_import

class excel_importer(object):
    """
    Abstract class of import excel
    """

    def __init__(self, file_path=None, excel_bin_value=None):
        # excel is excel file value, 
        self.excel_bin_value = excel_bin_value
        self.file_path = file_path
        if not file_path:
            self.prepare_file_path_from_bin_value()
        self.excel_data = {}
        self.value = {}
        self.read_excel()

    def prepare_file_path_from_bin_value(self):
        if self.excel_bin_value:
            # TODO
            self.file_path = '/tmp/file_name.xls'
        else:
            raise osv.except_osv(u'错误',u'请选择要导入的Excel文件!')
            
        return 

    def open_excel(self, file= 'file.xls'):
        try:
            data = xlrd.open_workbook(file)
            return data
        except Exception,e:
            print str(e)

    #根据索引获取Excel表格中的数据
    #参数:file：Excel文件路径
    #colnameindex：表头列名所在行的索引  ，by_index：表的索引
    def excel_table_byindex(
            self, file= 'file.xls', colnameindex=0, by_index=0
    ):
        data = self.open_excel(file)
        table = data.sheets()[by_index]
        nrows = table.nrows #行数
        ncols = table.ncols #列数
        colnames =  table.row_values(colnameindex) #某一行数据 
        data =[]
        for rownum in range(1,nrows):
            row = table.row_values(rownum)
            if row:
                data.append(row)
        return data

    #根据名称获取Excel表格中的数据   
    #参数:file：Excel文件路径     colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称
    def excel_table_byname(
            self, file= 'file.xls',colnameindex=0,by_name=u'Sheet1'
    ):
        data = self.open_excel(file)
        table = data.sheet_by_name(by_name)
        nrows = table.nrows #行数 
        ncols = table.ncols
        colnames =  table.row_values(colnameindex) #某一行数据 
        data =[]
        for rownum in range(1,nrows):
             row = table.row_values(rownum)
             if row:
                 data.append(row)
        return data

    def read_excel(self):
        table_name = 'Sheet1'
        table_index = 0
        if table_index>=0:
            self.excel_data = self.excel_table_byindex(
                file=self.file_path, colnameindex=0,by_index=table_index)
        elif table_name:
            self.excel_data = self.excel_table_byname(
                file=self.file_path,colnameindex=0, by_name=table_name)
        return

    #only use for test
    def get_excel_data(self):
        return self.excel_data

    #only use for test
    def prepare_value(self):
        return self.value

    def get_value(self):
        self.prepare_value()
        return self.value