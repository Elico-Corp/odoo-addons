# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{'name': 'Base Intercompany Sale',
 'version': '7.0.1.0.0',
 'category': 'Sales Management',
 'depends': ['base_intercompany', 'sale', 'purchase'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
This module is an extension designed to manage Inter-company Process (ICOPS)
and allows 2 companies to create Sale Orders and Purchase Order in each other.
     - Sale Order to Purchase Order (so2po)
     - Sale Order to Sale Order (so2so)
     - Purchase Order to Sale Order (po2so)
     - Handles the following events: Create, Update, Delete, Confirm and Cancel

TODO: demo data to be improved.\n
Blueprint: https://blueprints.launchpad.net/multi-company/+spec/icops
""",
 'images': [],
 'demo': ['base_intercompany_sale_demo.xml'],
 'data': ['security/ir.model.access.csv',
          'icops_model_view.xml',
          'sale_view.xml',
          'purchase_view.xml'],
 'installable': True,
 'application': False,
 }
