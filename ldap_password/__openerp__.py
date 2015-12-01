# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Basic ldap user management through Odoo',
    'version': '8.0.1.0.2',
    'depends': [
        'auth_ldap'
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'external_dependencies': {
        'python': ['ldap'],
    },
    'installable': True,
    'application': False
}
