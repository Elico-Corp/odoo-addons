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
{'name': 'Report printout improvement',
 'version': '0.1',
 'category': '',
 'depends': ['stock'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Report printout improvement
=============================
This module adds the sequence and total quantity
into the sales order, purchase order and delivery order printout

Usage
-----
* A new column is created to display the sequence.
* A new field diplays the total quantity.

Contributors
------------

* Siyuan Gu: gu.siyuan@elico-corp.com

""",
 'images': [],
 'demo': [],
 'data': ['views/stockpicking.xml',
          'views/saleorder.xml',
          'views/purchaseorder.xml',
          'views/purchasequotation.xml', ],
 'test': [],
 'installable': True,
 'application': False}
