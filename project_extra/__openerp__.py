# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Project Extra module',
    'version': '8.0.1.0.3',
    'category': 'Project Managements',
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn/',
    'depends': ['project', 'project_long_term'],
    'init_xml': [],
    'update_xml': [
            'project_view.xml',
            'project_data.xml',
            'security/ir.model.access.csv',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'certificate': '',
}
