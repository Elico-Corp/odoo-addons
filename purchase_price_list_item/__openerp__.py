# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Purchase Price List Item',
    'version': '7.0.1.0.0',
    'category': 'Purchase',
    'sequence': 19,
    'summary': 'Purchase Price List Item',
    'description': """ 
        Improve purchase price managment
        ================================

            * In Purchase List Item, the price is fixed based on price_surchage if base is 'fixed on UOP'
            * If 'fixed on UOP', if product UOP change, the price list price will be change automtically.
            * Add field 'Qty on Hand', and 'Stock Values' for product
            * Add field 'Qty on Hand', 'Stock Values', UOP in product list view

     """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['purchase'],
    'data': [
             'purchase_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}