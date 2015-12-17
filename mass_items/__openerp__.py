# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Add items of mass',
    'version': '8.0.1.0.1',
    'depends': [
        'sale',
        'purchase',
        'stock',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'wizard/mass_items.xml',
        'wizard/mass_items_confirm.xml',
        'wizard/mass_items_quantities.xml',
        'views/mass_items.xml',
        'views/quantity.xml',
    ],
    'installable': True,
    'application': False,
}
