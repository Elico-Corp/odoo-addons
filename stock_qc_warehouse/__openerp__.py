# -*- coding: utf-8 -*-
# © 2014 Elico Corp(https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Quality Management',
    'version': '7.0.1.0.0',
    'category': 'Quality Management',
    'sequence': 19,
    'summary': 'Process Stock Picking / Move by QC user / manager',
    'description': """
        Quality Management
        ==================
        Simple module to allow a control of the stock moves by the QC users.
        - This module adds 2 QC groups (user and manager) and create the QC check in location 
        - Only QC user / manager can process moves from a QC location

    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['stock', 'stock_location'],
    'data': [
        'security/qc_security.xml',
        'security/ir.model.access.csv',
        'stock_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}


