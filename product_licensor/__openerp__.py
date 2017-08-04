# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{'name': 'Product Licensor',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['product', 'purchase'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
 :alt: License

This module adds licensors for the products,

- add a reporting;

- add a new group: Product licensor manager to manage licensors.

- add a new menu: purchase/licensors to view licensors

usage
=====
- User needs to belong to the group:
Product licensor manager to setup the licensors.
""",
 'data': [
     'security/product_licensor_security.xml',
     'security/ir.model.access.csv',
     'licensor_view.xml',
     'product_view.xml',
     'report/product_licensor_report_view.xml'],
 'installable': True,
 'application': False,
 }
