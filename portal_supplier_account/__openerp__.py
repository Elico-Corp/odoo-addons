# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Kevin Lee<kevin.lee@elico-corp.com>
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
    'name': 'Portal Supplier Account',
    'version': '1.0',
    'category': '',
    'summary': '',
    'description': """
Portal Supplier Management.
====================================

New gorup: Portal Supplier Account
--------------------------------------------
    * manage own products
    * modify own profile data
    """,
    'author': 'Elico Corp',
    'website': 'http://www.openerp.com',
    'images': [],
    'depends': [
        'portal_sale', 'magentoerpconnect_catalog', 'stock'
    ],
    'data': [
        'wizard/change_supplier_qty.xml',
        'product_view.xml',
        'res_partner_view.xml',
        'group_portal_supplier.xml',
        'menu_portal_supplier.xml',
        'security/ir.model.access.csv',
        'security/supplier_portal_account.xml',
    ],
    'installable': True,
}
