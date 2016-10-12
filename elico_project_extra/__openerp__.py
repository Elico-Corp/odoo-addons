# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Project Extra module',
    'version': '0.3',
    'category': 'Project Managements',
    'description': """
        * set color yellow for high priority task, set color red for task in delay.
        * add parnter prefix for task name, in kanban view and tree view.
        * set default stage (first, last)for action: open task and close task, 
        """,
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn/',
    'depends': ['project','project_long_term'],
    'init_xml': [],
    'update_xml': [
            'project_view.xml',
            'project_data.xml',
            'security/ir.model.access.csv',
        ],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
