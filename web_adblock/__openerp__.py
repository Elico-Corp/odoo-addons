# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'OpenERP Adblock',
    'version': '7.0.1.0.0',
    'category': 'Web',
    'depends': ['mail'],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'description': """
        Module which hides the OpenERP announcement bar.
    """,
    'images': [],
    'js': ['static/src/js/announcement.js'],
    'installable': True,
    'application': False,
}
