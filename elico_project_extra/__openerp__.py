# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author: LIN Yu <lin.yu@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Project Extra module for Elico Corp',
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
