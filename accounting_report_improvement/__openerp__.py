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
{'name': 'Account Reoprt Improvement',
 'version': '0.1',
 'category': '',
 'depends': ['point_of_sale'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Account report improvement
===================================
This model adds a new field cost in

* Invoice analysis
* POS sale analysis
* Account move


Usage
-----
A new field displays cost for the product

Contributors
------------

* Siyuan Gu: gu.siyuan@elico-corp.com
""",
 'images': [],
 'demo': [],
 'data': ['views/account_view.xml'],
 'test': [],
 'installable': True,
 'application': False}
