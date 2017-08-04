# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Stock Pack Wizard',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': '',
    'description' : """
        This module add new functionalities to Pack:
        
        Split Pack at picking and picking_line
       
        New fields added to pack:
        - Customer Reference: Customer code
        - Fullname: Customer Code + Sequence
        - Address: Customer Address
        - Dimensions: L, W, H, CBM
        - Weights: NW and GW
        
        New object created:
        - Pack Template:
            - Name and Code
            - Dimensions: L, W, H, CBM
            - Weights: NW and GW
        
        Wizard created: a wizard will let user assign Stock Moves to Pack
        
        Report created: Packing List (can be printed from Pack Tree view)
    
    """,
    'depends': ['base','stock','report_webkit'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'product_ul_view.xml',
        'stock_tracking_view.xml',
        'wizard/wizard_picking_tracking_view.xml', 
        'stock_picking_view.xml',

        'stock_tracking_report.xml',
         'data/product.ul.csv',
        ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
