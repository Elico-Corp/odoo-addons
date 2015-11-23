# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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

{'name': 'Pos Session Customer Payment Details',
 'version': '1.0',
 'category': 'Generic Modules',
 'depends': ['point_of_sale', 'account_accountant'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
 .. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
     :alt: License

 POS Session Customer Payment Details
 ====================================

 By using our module, you can find the payment
 details for different VIP customers
 for POS in the bank statement form view and customer payment details.

 Usage
 =====
  On POS session, we have an extra lines of bank statements.

 Contributors
 ------------

 * Alex Duan: alex.duan@elico-corp.com

 .. image:: http://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: http://odoo-community.org
""",
 'images': [],
 'demo': [],
 'data': ['view/pos_session_view.xml'],
 'installable': True,
 'application': False,
 }
