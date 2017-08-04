# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Gap Analysis Project',
    'version': '7.0.1.0.0',
    'category': 'Tools',
    'complexity': "easy",
    'description': """
This module provides the necessary tools to generate a new project with all the task from the Gap Analysis.
""",
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images': [],
    'depends': ['gap_analysis'],
    'init_xml': [],
    'update_xml': [
        'gap_analysis_project.xml',
        'security/ir.model.access.csv',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'active': True,
    'certificate': '',
}

