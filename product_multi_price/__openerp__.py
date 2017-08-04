# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# © 2014 Akretion Sébastien BEAU (sebastien.beau@akretion.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'product_multi_price',
    'version': '7.0.1.0.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """empty""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['product','account', 'sale','product_prices_on_variant'],
    'init_xml': [],
    'update_xml': [
           'product_price_fields_view.xml',
           'product_view.xml',
           'product_price_field_config.xml',
           'account_view.xml',
           'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': False,
    'active': False,
}

