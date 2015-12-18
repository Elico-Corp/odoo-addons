# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Order item sequence and total quantity',
    'version': '8.0.1.0.2',
    'category': 'pos',
    'depends': [
        'point_of_sale',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'views/pos_quantity.xml',
    ],
    'qweb': [
        'static/src/xml/quantity.xml',
    ],
    'installable': True,
    'application': False}
