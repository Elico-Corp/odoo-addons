# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Purchase stock journal ',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['stock', 'purchase'],
    'category': 'Generic Modules/Others',
    'description': """
This module add field on warehouse and pass from SO to DO..
=========================================
A stock journal should be assigned per warehouse and
    used in the DO created from the SO.
Add field at warehouse level (not mandatory)
Modify the method to create the stock picking to include the
    journal from shop/warehouse (if there is one)
      """,
    'data': ['stock_view.xml'],
    'auto_install': False,
    'installable': True,
    'active': True,
}
