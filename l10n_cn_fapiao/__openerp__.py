# -*- coding: utf-8 -*-
# © 2004-2010 Tiny SPRL (http://tiny.be)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Chinese Fapiao Management',
    'version': '7.0.1.0.0',
    'category': 'Accounting',
    'sequence': 19,
    'summary': 'Chinese Fapiao Management and link with OpenERP Invoice',
    'description': """

        * "Fapiao" is an official invoice in China, printed in a separate official software.
        * This module allows the users to manage all emitted and received "fapiao"  as object in OpenERP. It has no impact on accounting books and doesnot (yet) integrate with external official software. It adds new submenu called Fapiao under the menu Accounting.

        The procedure to follow for the fapiao management is as below:
        * Step 1: A fapiao is received or emitted
        * Step 2: The document can be scanned as image
        * Step 3: A new fapiao is created in OpenERP
        * Step 4: The scanned document is uploaded to the newly created object as attachment.
        * Step 5: Fapiao allocation to invoice: Fapiao and OpenERP invoices can be linked to each other
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images': [],
    'depends': ['account'],
    'data': [
        'fapiao_view.xml',
        'security/ir.model.access.csv',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

