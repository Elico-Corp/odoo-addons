# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Chen rong <chen.rong@elico-corp.com>

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

{'name': 'Warehouse Management Extend',
 'version': '1.0',
 'category': '',
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """

 print product barcode 
""",
 'images': [],
 'demo': [],
 'depends': ['stock','mrp',],
 'data': ['stock_report.xml','views/report_stockpicking.xml','views/stock.xml',
          'wizard/import_excel_view.xml','stock_view.xml',
          'views/report_stock_lot_barcode.xml',
          'stock_data.xml','wizard/print_product_barcode.xml'],
 'installable': True,
 'application': False,
 }