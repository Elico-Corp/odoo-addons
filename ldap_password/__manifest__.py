# -*- coding: utf-8 -*-
# © 2015-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Basic Ldap User Management Through Odoo',
    'summary': 'Basic Ldap User Management Through Odoo',
    'version': '10.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': ['ldap'],
    },
    'depends': [
        'auth_ldap'
    ],
    'installable': True,
}
