# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Raw Material change in MO',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'http://www.openerp.com.cn',
    'category': 'Manufacturing',
    'sequence': 18,
    'summary': 'MRP support Add or Cancel the moves',
    'images': [],
    'depends': ['mrp','procurement', 'stock'],
    'description': """
        Add or Cancel the Raw Material moves in MO
        ===========================================

        The module allows you to:
        * Add new products to consume in a confirmed MO.
        * Cancel products to consume in a confirmed MO.

    """,
    'data': [
        'mrp_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

