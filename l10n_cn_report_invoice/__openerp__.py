# -*- coding: utf-8 -*-
# © 2004-2010 Tiny SPRL (http://tiny.be)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Chinese/English Invoice',
    'version': '7.0.1.0.0',
    'category': 'custom',
    'sequence': 19,
    'summary': 'Chinese/English Bilingual Invoice Reports',
    'description': """
        Chinese/English Bilingual Invoice Reports
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['account'],
    'data': [
        'elico_reports_view.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

