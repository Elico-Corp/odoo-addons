# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Portal Supplier Delivery Order',
    'version': '7.0.1.0.0',
    'description': """
        Portal Supplier can deliver his own Delivery Order
        (defined by sale man of DO, taken from sals man of SO).

        """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['sale_stock', 'portal'],
    'data': [
        'view_portal_supplier_stock.xml',
        'menu_portal_stock.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
