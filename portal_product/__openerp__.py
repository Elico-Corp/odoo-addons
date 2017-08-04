# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Portal Product',
    'version': '7.0.1.0.0',
    'author': 'Elico',
    'website': 'https://www.elico-corp.com',
    'depends': ['product', 'portal'],
    'data': [
        'view_portal_product.xml',
        'menu_portal_product.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
