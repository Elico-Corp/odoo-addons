# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#    Jon Chow <jon.chow@elico-corp.com>
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

{
    'name': 'Stock Pack Wizard',
    'version': '1.0',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description': """
    This module add new functionalities to Pack:

    Split Pack at picking and picking_line

    New fields added to pack:
    - Customer Reference: Customer code
    - Fullname: Customer Code + Sequence
    - Address: Customer Address
    - Dimensions: L, W, H, CBM
    - Weights: NW and GW

    New object created:
    - Pack Template:
        - Name and Code
        - Dimensions: L, W, H, CBM
        - Weights: NW and GW

    Wizard created: a wizard will let user assign Stock Moves to pack
    Report created: Packing List (can be printed from Pack Tree view)

    """,
    # depends on sale_stock to have the field:sale_id from stock.picking model.
    'depends': ['sale_stock', 'report_webkit'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'product_ul_view.xml',
        'stock_tracking_view.xml',
        'wizard/wizard_picking_tracking_view.xml',
        'stock_picking_view.xml',
        'stock_tracking_report.xml',
        'data/product.ul.csv',
    ],
    'test': ['test/test_pack_wizard.yml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
