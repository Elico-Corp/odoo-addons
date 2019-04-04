# © 2015-2019 Elico corp (www.elico-corp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Website Captcha',
    'version': '12.0.1.0.0',
    'category': 'Website',
    'depends': [
        'website',
    ],
    'author': 'Elico Corp',
    'license': 'LGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'views/website_templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'external_dependencies': {
        'python': ['captcha', 'simplecrypt'],
    },
    'installable': True,
    'auto_install': False
}
