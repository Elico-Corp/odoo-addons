# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{'name': 'Base Intercompany',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['connector'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
This module is the structure designed to manage Inter-company Process (ICOPS)
and allows 2 companies to create objects in each other.
This module needs to be installed with one of the following modules:
     - Base Intercompany Sale
     - Base Intercompany Stock (in development)
     - Any module which extends the Base Intercompany module

TODO: demo data to be improved.\n
Blueprint: https://blueprints.launchpad.net/multi-company/+spec/icops
""",
 'images': [],
 'demo': ['base_intercompany_demo.xml'],
 'data': ['security/ir.model.access.csv',
          'icops_model_view.xml',
          'base_intercompany_menu.xml'],
 'installable': True,
 'application': False,
 }
