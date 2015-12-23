# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Compute the number of products which can be produced',
    'version': '8.0.1.0.0',
    'depends': [
        'stock',
        'mrp',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'description': """
    """,
    'data': [
        'wizard/check_product_qty_wizard.xml',
        'product_view.xml',
    ],
    'installable': True,
    'application': False,
}
