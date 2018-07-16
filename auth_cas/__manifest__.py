# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'CAS Authentication',
    'version': '8.0.1.0.0',
    'category': 'Authentication',
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'support': 'support@elico-corp.com',
    'website': 'https://www.elico-corp.com/',
    'depends': ['base', 'base_setup', 'web'],
    'data': ['res_config_view.xml', 'views/auth_cas_view.xml'],
    'external_dependencies': {'python': ['pycas']},
    'images': [
        'images/cas_auth_settings.jpeg',
        'images/cas_auth_example_login_page.jpeg'],
    'auto_install': False,
    'installable': True,
    'bootstrap': True,
}
