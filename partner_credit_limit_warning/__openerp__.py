# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Check Partner credit limit',
    'version': '7.0.1.0.0',
    'category': 'Sales',
    'description': """
        Check the credit limit of the customer and:
        - Adds one warning when clicking on SO confirm button
        - block the delivery order process button.
        Allows a manager to authorize the delivery 
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': ['sale', 'sale_quotation', 'stock'],
    'update_xml': [
        'stock_view.xml',
        'wizard/sale_confirm_warning.xml',
    ],
    'installable': True,
    'active': False,
}
