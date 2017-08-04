# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{'name': 'sale_cancel',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['sale'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
 Check if any of the delivery is in done state (including chained):
    in this case not possible to cancel
    otherwise cancel first all delivery and chained moves + SO
""",
 'data': ['sale_view.xml'],
 'installable': True,
 'application': False,
 }
