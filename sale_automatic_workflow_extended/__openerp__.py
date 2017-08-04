# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{'name': 'Sale Automatic Workflow Extended',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['sale_automatic_workflow', 'sale', 'crm'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
 This module extends the community module: sale_automatic_workflow,
 allowing create automatic invoice after delivery order.
""",
 'data': ['sale_automatic_workflow_extended_view.xml'],
 'installable': True,
 'application': False,
 }
