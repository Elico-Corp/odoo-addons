# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Bundle product',
    'version': '7.0.1.0.0',
    'category': 'Sales Management',
    'description': """
    This allow you to create bundle product, which is a product containing other products.

    Example: 
    "Drinks Set"
      - 1 Apple Juice
      - 1 Orange Juice
      - 1 Grape Juice
    
    On the Sale Order will appear "Drinks Set", and on the Packing list will appear the detail of the Bundle.
    You can replace one of the item in the Bundle in the Delivery Order, eg: replace 1 Orange Juice by 1 Mandarin Orange Juice.
    
    When defining your Bundle product, you can specify the revenue repartition within the bundle items.
    This addon doesn't use the BoM, so no MO generated. 
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['sale_stock'], 
    'init_xml': [],
    'update_xml': [
           'security/ir.model.access.csv',
           'product_view.xml',

    ],
    'demo_xml': [],
    'installable': True,
    'active': True,
}


