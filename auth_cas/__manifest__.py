# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016-2018 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'CAS Authentication',
    'version': '10.0.1.0.0',
    'category': 'Authentication',
    'summary': 'CAS Authentication',
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'support': 'support@elico-corp.com',
    'website': 'https://www.elico-corp.com/',
    'depends': [
        'base_setup',
        'web'
    ],
    'data': [
        'wizard/res_config_view.xml',
        'views/auth_cas_view.xml'
    ],
    'images': [
        'images/cas_auth_settings.jpeg',
        'images/cas_auth_example_login_page.jpeg'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
