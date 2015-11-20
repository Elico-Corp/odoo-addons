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
{'name': 'Website sales order and reservation process',
 'version': '0.1',
 'category': '',
 'depends': ['website_sale',
             'website_sale_collapse_categories',
             'theme_loftspace'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Sales order and reservation process
======================================================================
This model does the below updates for websit_sale:
    * remove the string "Taxes" in shopping cart and payment
    * Disable the "Add to cart" button and show button "预定"
      when product quantity isn't available.
    * add the description and inventory status in shopping cart page
    * add the add the description and inventory status in payment page
    * delete the product description in the shopping cart.
    * only search the product name in the search function
    * remove the odoo information in the footer

Contributors
----------------------------------------------------------------------

* Siyuan Gu: gu.siyuan@elico-corp.com

""",
 'images': [],
 'demo': [],
 'data': ['views/templates_inherit.xml'],
 'test': [],
 'installable': True,
 'application': False}
