# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Purchase Order Approvement',
    'version': '7.0.1.0.0',
    'category': 'Purchases',
    'description': """
        Button on PO will pop a question, give the operator a possibility to confirm.
    """,
    'author': 'Elico Corp',
    'website': 'www.elico-corp.com',
    'depends': ['purchase'],
    'update_xml': [
        'purchase_confirm_view.xml',
    ],
    'installable': True,
    'active': False,
}
