#-*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)



{
    'name': 'Stock report slow-moving',
    'version': '7.0.1.0.0',
    'category': 'Custom',
    'description': """

This is a slow-moving analysis report aimed to classified the products according 
to their stock rotation	in order to identify slow-moving products. 
	
	- Add a scheduler has been added to create a table nightly
	- This report is based on webkit
	- only displays references with stock
     """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['base', 'product', 'stock', 'sale', 'purchase', 'mrp',
        'report_webkit',
        'base_headers_webkit'],
    'update_xml': [
        'security/ir.model.access.csv',
        'stock_slowmoving_view.xml',
        'stock_slowmoving_report_view.xml',
        'wizard/stock_slowing_move_view.xml',
    ],
    'installable': True,
    'active': False,
}
