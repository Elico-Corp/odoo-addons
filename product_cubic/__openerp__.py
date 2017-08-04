# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Product cubic',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp ',
    'depends': ['product'],
    'category': 'Generic Modules/Others',
    'description': """
This module adds fields to product
=========================================
new fields:
    * height
    * legth
    * width
    * cubic_weight: height/100.0 * width/100.0 * length/100.0 * 250.0
      """,
    'data': ['product_view.xml'],
    'auto_install': False,
    'installable': True,
    'active': True,
}
