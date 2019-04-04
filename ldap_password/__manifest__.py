# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Basic Ldap User Management Through Odoo',
    'summary': 'Basic Ldap User Management Through Odoo',
    'version': '12.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['ldap'],
    },
    'depends': [
        'auth_ldap'
    ],
    'installable': True,
}
