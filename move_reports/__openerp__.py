# -*- coding: utf-8 -*-
# © 2004-2010 Tiny SPRL (http://tiny.be).
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': ' Move Report',
    'version': '7.0.1.0.0',
    'category': 'custom',
    'sequence': 1,
    'summary': 'Move Reports',
    'description': """
        Custom Reports:
        ===============

        python lib dependancy : xlsxwriter.
         * Purchase Order
         * RFQ
         * Picking
         * Move Report ()
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['stock_with_cost','product_stock_type'],
    'data': [        
        'stock_move_report/stock_move_report_view.xml',
        'security/ir.model.access.csv',
    ],
    'test': [
        
    ],
    'demo': [
       
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

