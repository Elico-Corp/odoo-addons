# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Multicompany - Easy Switch Company',
    'version': '8.0.1.0.0',
    'category': 'web',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'web',
    ],
    'data': [
        'view/res_users_view.xml',
    ],
    'qweb': [
        'static/src/xml/switch_company.xml',
    ],
    'installable': True,
    'auto_install': False,
}
