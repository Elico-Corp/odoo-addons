# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2014 Elico Corp (<http://www.elico-corp.com>)
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
{'name': 'Timesheet Activities Report',
 'version': '0.1',
 'category': 'Human Resources',
 'depends': ['hr_timesheet', 'project_timesheet', 'project_issue_sheet'],
 'author': 'Elico Corp,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'images': [],
 'demo': [],
 'data': ['report/timesheet_activity_report_view.xml',
          'security/ir.model.access.csv'],
 'installable': True,
 'application': False}
