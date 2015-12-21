# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'POS printout improvement',
    'version': '8.0.1.0.1',
    'category': 'POS',
    'depends': [
        'pos_membership',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'views/js.xml',
    ],
    'qweb': [
        'static/src/xml/printout.xml',
    ],
    'installable': True,
    'application': False,
}
