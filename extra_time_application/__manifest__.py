# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# Elico Proprietary License v1.0.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Extra Time Application',
    'version': '10.0.0.0.0',
    'author': "Elico Corp",
    'website': 'https://www.elico-corp.com',
    'license': 'Other proprietary',
    'support': 'https://support@elico-corp.com',
    'depends': [
        'project',
    ],
    'data': [
        'wizard/time_prompt_view.xml',
        'views/extra_time_approve_view.xml',
        'views/project_task_form_inherit.xml',
        'security/extra_time_application_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
