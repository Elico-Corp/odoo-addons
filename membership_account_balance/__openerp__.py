# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Siyuan Gu / Alex Duan
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
{'name': 'Membership Management - Member Account Balance',
 'version': '0.1',
 'category': '',
 'depends': ['account', 'membership', 'base_setup'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Membership Management - Member Account Balance
=======================================================
This model adds a check box for membership in account.
And calculate the total membership in customer.

Technical Notes (Please ignore if you are functional)
=====================================================
 - This module total rewrites the following methods:
    * debit and credit fields compute function on model: res_partner.
 - Tricks
    * This module still uses V7 API since need to
    overwrite some compute functions on model: res_partner;

Usage
-----
A new check box records the membership for the account.
(Default is not membership)

Total membership is calculated in the customer.

Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>
* Siyuan Gu: <gu.siyuan@elico-corp.com>
""",
 'images': [],
 'demo': [],
 'data': ['views/account_view.xml',
          'views/partner_view.xml'],
 'test': [],
 'installable': True,
 'application': False}
