# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Purchase Enhancements',
    'version': '7.0.1.0.0',
    'category': 'Purchase',
    'sequence': 19,
    'summary': 'Allow several enhancements on purchase management',
    'description': """
        Purchase management enhancements
        ==================================================
        ** 2 new check for price control: one at supplier level, on at Product level: both False/Unchecked means user cannot change the price in PO Line

        ** New Price list calculation scheme based on the UoP: if chosen, user needs only to input the "Surcharge" field and price is refered to UoP.

        ** Efficient Search list per PO line

        ** Improved Header addresses.


    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['product', 'purchase'],
    'data': [
             
        'security/ir.model.access.csv',
        'purchase_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
