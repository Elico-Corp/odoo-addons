# -*- coding: utf-8 -*-
# © 2016 Roméo Guillot Roméo Guillot (http://www.opensource-elanz.fr).
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'CAS Authentication',
    'version': '1.0',
    'category': 'Authentication',
    'description': """""",
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com/',
    'depends': ['base', 'base_setup', 'web'],
    'data': ['res_config_view.xml', 'views/auth_cas_view.xml'],
    'images': [
        'images/cas_auth_settings.jpeg',
        'images/cas_auth_example_login_page.jpeg'],
    'auto_install': False,
    'installable': True,
    'bootstrap': True,
}
