# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: LIN Yu <lin.yu@elico-corp.com>
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
    'name': 'Sale Order Line',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 19,
    'summary': 'Sale Order Line',
    'description': """
    Standard OpenERP manages Sales by Orders.
    
    In Sales Module after Sales Order Menu,
    it was added Sales by Product Menu.
    User will open a tree view displaying SOLs,
    with group by Product set as default Group.

    Main Information Displayed:
    - Order Reference (and icon to open it)
    - Customer
    - Quantity
    - Final Quantity (to be added)
    - Order Status
    - Product State
    - Product Type
    According to Product State, lines will have different colors:
    - Red: Catalogue, 
    - Yellow (orange for viewing purposes): Preorder
    - Green: Order
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images': [],
    'depends': ['product', 'purchase', 'warning', 'mmx_product_advance', 'sale_menu'],
    'data': [
        'security/ir.model.access.csv',
        'sale_view.xml',
        #'wizard/wizard_update_qty_store_view.xml',
    ],
    'test': [],
    'demo': [],
    'css': ['static/src/css/sale_order_line.css', ],
    #'js':['static/src/js/sale_order_line.js',],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
