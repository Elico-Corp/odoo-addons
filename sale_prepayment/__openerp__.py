# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{'name': 'sale_prepayment',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['sale_automatic_workflow', 'sale_payment_method', 'sale_payment_prepayment'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
This module do the prepayment on Sale Quotations.
""",
 'data': ['wizard/prepay_wizard_view.xml', 'sale_view.xml'],
 'installable': True,
 'application': False,
 }
