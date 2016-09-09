# -*- coding: utf-8 -*-
#   2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Timesheet Activities Report',
 'version': '8.0.1.2.0',
 'category': 'Human Resources',
 'depends': [
     'project_timesheet',
     'project_issue_sheet',
     'project_task_category',
     'project_project_category',
     'business_requirement'
 ],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'images': [],
 'demo': [],
 'data': ['report/timesheet_activity_report_view.xml',
          'security/ir.model.access.csv'],
 'installable': True,
 'application': False}
