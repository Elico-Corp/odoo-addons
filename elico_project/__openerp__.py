# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Sebastien Maillard
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
    'name': 'Elico Project',
    'version': '0.1',
    'category': '',
    'depends': [
        'project_timesheet',
        'project_issue_sheet'
    ],
    'author': 'Elico Corp,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'images': [],
    'demo': ['project_demo.xml'],
    'data': [
        'project_task_view.xml',
        'project_issue_view.xml',
        'project_timesheet_view.xml',
        'project_tasks_planning_view.xml',
        'reset_planning_wizard_view.xml'
    ],
    'test': [],
    'installable': True,
    'application': False
}
