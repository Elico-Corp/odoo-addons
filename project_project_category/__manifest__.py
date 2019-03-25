# © 2016-2019 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Configurable Category",
    "version": "12.0.1.0.0",
    'category': 'Project Management',
    'website': 'https://www.elico-corp.com',
    'support': 'support@elico-corp.com',
    "author": "Elico corp",
    "license": "LGPL-3",
    "depends": [
        "project",
    ],
    "data": [
        'data/project_project_category_data.xml',
        'security/ir.model.access.csv',
        'views/project_project_view.xml',
        'views/project_project_category_view.xml',
    ],
    "installable": True,
}
