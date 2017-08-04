# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Gap Analysis Aeroo Report',
    'version': '7.0.1.0.0',
    'category': 'Tools',
    'complexity': "easy",
    'description': """
        Generate a gap-analysis with cost estimation
        --------------------------------------------

        To generate .xls instead of .ods
        ---------------------------------
        download and install report_aeroo_ooo

        Current addon Limit
        -------------------
        The columns are not managed dynamically, so the you can make a report with <= 6 workload type.
        You can have more workload type used in your gap analysis, but they won't be shown. 
             
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images': ['images/report.jpg'],
    'depends': ['gap_analysis_project_long_term','report_aeroo'],
    'init_xml': [],
    'update_xml': [
        'wizard/wizard_view.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'active': True,
    
}


