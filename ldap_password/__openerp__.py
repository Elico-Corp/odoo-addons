# -*- coding: utf-8 -*-
# © <2010-2014> <Augustin Cisterne-Kaas>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Basic ldap user management through Odoo',
    'version': '8.0.1.0.0',
    'depends': [
        'auth_ldap'
    ],
    'author': 'Elico Corp,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'external_dependencies': {
        'python': [
            'ldap',
        ],
    },
    'installable': True,
    'application': False
}
