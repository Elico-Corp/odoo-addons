# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Website Forum Nutrition',
    'version': '0.1',
    'category': '',
    'depends': [
        'website_forum',
        'website_sale',
        'sale',
        'product'
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Website Forum Nutrition
=======================

This module:
    * adds a new model: `product.symptom`, which is secondary product
category.
    * adds a new field: symptom_ids on model: `product_template`
    * add a new menu under `forum`: Healthy Menu
    * add new page to display all the symptoms.
    * add a new page to display all the products.

Installation
============

 Normal way of installation.

Usage
=====

 * Go to `Sales` -> `Configuration` -> `Product Categories & Attributes`
    -> `Symptom`, create new symptoms as you need.
 * Go to `product template` form, assign the symptoms as you need.

Contributors
------------

* Alex Duan: alex.duan@elico-corp.com

    """,
    'images': [],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/product_symptom_view.xml',
        'views/template.xml'
    ],
    'test': [],
    'installable': True,
    'application': False
}
