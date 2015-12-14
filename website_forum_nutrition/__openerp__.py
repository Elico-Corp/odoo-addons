# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website Forum Nutrition',
    'version': '8.0.1.0.1',
    'category': 'website',
    'depends': [
        'website_forum',
        'website_sale',
        'sale',
        'product',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'security/ir.model.access.csv',
        'views/product_symptom_view.xml',
        'views/template.xml',
    ],
    'installable': True,
    'application': False
}
