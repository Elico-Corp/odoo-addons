# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2014 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>

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

{'name': 'Product Licensor',
 'version': '1.0',
 'category': 'Generic Modules',
 'depends': ['product', 'purchase'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
 :alt: License

This module adds licensors for the products,

- add a reporting;

- add a new group: Product licensor manager to manage licensors.

- add a new menu: purchase/licensors to view licensors

usage
=====
- User needs to belong to the group:
Product licensor manager to setup the licensors.
""",
 'images': [],
 'demo': [],
 'data': [
     'security/product_licensor_security.xml',
     'security/ir.model.access.csv',
     'licensor_view.xml',
     'product_view.xml',
     'report/product_licensor_report_view.xml'],
 'installable': True,
 'application': False,
 }
