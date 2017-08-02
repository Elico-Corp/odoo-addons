# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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
    'name': 'Gap Analysis',
    'version': '1.0',
    'category': 'Tools',
    'complexity': "easy",
    'description': """
This module provides the necessary tools to create and manage your gap-analysis.
=> Once the Gap Analysis set as Done, you can generate a new project with all the task from the Gap Analysis.


You can manage :
----------------
* functionalities, eg: "Ability to provide quantity discount"
* categories,      eg: "SEO, Website, ..."
* workload,        eg: "1 day for 500$"
* workload type,   eg: "Training, Advanced Development, ..."


Report :
--------
* Generate a full gap-analysis, with the total planned workload and cost estimation.


Security :
----------
* Everybody can read
* Gap Analysis Users can create, read and update their own gap-analysis
* Gap Analysis Managers can create, read, update and delete any gap-analysis
""",
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'images': ['images/report.jpg','images/gap_analysis.jpg','images/gap_analysis2.jpg'],
    'depends': ['report_webkit','project'],
    'init_xml': [],
    'update_xml': [
        'security/gap_analysis_rules.xml',
        'security/ir.model.access.csv',
        'report/gap_analysis_report_view.xml',
        #'gap_analysis_workflow.xml',
        'gap_analysis_sequence.xml',
        'gap_analysis.xml',
        'wizard/import_from_tmpl.xml',
        'wizard/line_create_wizard_view.xml'
	],
    #'demo_xml': ['gap_analysis_demo.xml'], 
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': True,
    'certificate': '',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
