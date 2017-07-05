# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (http://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project Planning',
    'version': '8.0.1.0.0',
    'category': 'Project',
    'depends': [
        'project_task_type',
        'project_task_wbs',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'project_task_view.xml',
        'project_tasks_planning_view.xml',
        'reset_planning_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}
