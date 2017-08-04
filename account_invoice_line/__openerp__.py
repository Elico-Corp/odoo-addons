# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Invoice Line',
    'version': '7.0.1.0.0',
    'category': 'Account',
    'sequence': 19,
    'summary': 'Invoice line',
    'description': """
Invoice Line
==================================================
* Add Account Invoice Line View
* Add Account Invoice Type
* Add Several New Fields to Invoice supplier_invoice_number, fapiao_date, partner_ref, reference_type
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['account'],
    'data': [
        'account_view.xml',        
        'security/ir.model.access.csv',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: