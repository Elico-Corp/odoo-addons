# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    xiexiaopeng <xie.xiaopeng@elico-corp.com>
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
    'name': 'Stock PMC Report',
    'version': '1.0',
    'category': '',
    # depends sale_extra is_draft field,
    'depends': [
        'sale_extra',
        'purchase',
        'stock',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'description': """
        Module which hides the OpenERP announcement bar.
    """,
    'data': [
        'stock_view.xml',
        'wizard/stock_inventory_report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}