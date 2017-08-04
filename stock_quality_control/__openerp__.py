# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
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
        Process Stock Picking / Move by QC user / manager
        * Add Group QC Manager \ QC user
        * Link QC location with manual chained picking. 
        * Check when location update
        * Check when update push flow
        * Add a flag qc_picking to picking when it is a qc picking.

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

