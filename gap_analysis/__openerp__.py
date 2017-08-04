# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Gap Analysis',
    'version': '7.0.1.0.0',
    'category': 'Tools',
    'complexity': "easy",
    'description': """
        This module provides the necessary tools to create and manage your gap-analysis.
        Once the Gap Analysis set as Done, you can generate a new project with all the task from the Gap Analysis.


        You can manage
        --------------
        * functionalities, eg: "Ability to provide quantity discount"
        * categories,      eg: "SEO, Website, ..."
        * workload,        eg: "1 day for 500$"
        * workload type,   eg: "Training, Advanced Development, ..."


        Report
        ------
        * Generate a full gap-analysis, with the total planned workload and cost estimation.


        Security
        --------
        * Everybody can read
        * Gap Analysis Users can create, read and update their own gap-analysis
        * Gap Analysis Managers can create, read, update and delete any gap-analysis
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
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
	],
    'demo_xml': ['gap_analysis_demo.xml'], 
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': True,

}


