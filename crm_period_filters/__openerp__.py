# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'CRM period filters',
    'version': '8.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': '',
    'description': """
         access rule: case
    """,
    'depends': ['base', 'crm'],
    'category': '',
    'sequence': 10,
    'data': [
        'crm_view.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
