# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Sales Bottom Price Management',
    'version': '7.0.1.0.0',
    'category': 'Sales Management',
    'summary': 'Sales Bottom Price Management',
    'description': """ Sales Bottom Price Management  """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'depends': [
        'sale_sample',
        'sale',
        'product',
        'sale_stock',
        'account',
        'stock',
        'account_accountant'],
    'data': ['sale_view.xml'],
    'installable': True,
    'auto_install': False,
}


