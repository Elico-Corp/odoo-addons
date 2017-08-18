# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Configurable Category",
    "version": "10.0.1.0.0",
    'category': 'Project Management',
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    "author": "Elico corp",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "depends": [
        "project",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/project_project_view.xml',
        'views/project_project_category_view.xml',
    ],
}
