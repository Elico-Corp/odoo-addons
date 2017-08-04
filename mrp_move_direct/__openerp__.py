# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'MRP support Add or Cancel the moves.',
    'version': '7.0.1.0.0',
    'author': 'Andy Lu',
    'website': 'http://www.openerp.com.cn',
    'category': 'Manufacturing',
    'sequence': 18,
    'summary': 'MRP support Add or Cancel the moves',
    'images': [],
    'depends': ['mrp','procurement', 'stock'],
    'description': """
        MRP support Add or Cancel the moves in OpenERP
        ===========================================

        The module allows you to:
        * Add new products to consume directly.
        * Cancel(Scrap) products to consume directly.
        * recalculate cost

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

