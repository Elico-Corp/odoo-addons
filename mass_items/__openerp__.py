# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Siyuan Gu
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
{'name': 'Add items of mass',
 'version': '0.1',
 'category': '',
 'depends': ['sale', 'purchase', 'stock'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Add items of mass
=================
This model allows to add items of mass and
displays the total quantity in below models:

* Sales
* Purchases
* Warehouse

Usage
-----
A new button "Add items" is added in the title bar
when user create a draft.

This button is linked to a wizard which allows user
adds product items of mass.

The wizard displays below attributes of the product:

* Internal Reference
* Name
* Internal category
* EAN13 Barcode

A new attribute contains the total quantity in the bottom
of the list

Contributors
------------

* Siyuan Gu: gu.siyuan@elico-corp.com

""",
 'images': [],
 'demo': [],
 'data': [
     'wizard/mass_items.xml',
     'wizard/mass_items_confirm.xml',
     'wizard/mass_items_quantities.xml',
     'views/mass_items.xml',
     'views/quantity.xml'
 ],
 'test': [],
 'installable': True,
 'application': False}
