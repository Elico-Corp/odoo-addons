# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website sales order and reservation process',
    'version': '8.0.1.0.1',
    'category': 'web',
    'depends': [
        'website_sale',
        'website_sale_collapse_categories',
        'theme_loftspace',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'views/templates_inherit.xml',
    ],
    'installable': True,
    'application': False,
}
