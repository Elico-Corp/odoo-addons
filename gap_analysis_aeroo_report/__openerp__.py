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
    'name': 'Gap Analysis Aeroo Report',
    'version': '1.0',
    'category': 'Tools',
    'complexity': "easy",
    'description': """
This module generate a full gap-analysis in .ods with the cost estimation.

To generate .xls instead of .ods:
---------------------------------
1- download and install report_aeroo_ooo
2- download
3- download
4- download


Current addon Limit: 
--------------------
The columns are not managed dynamically, so the you can make a report with <= 6 workload type.
You can have more workload type used in your gap analysis, but they won't be shown. 

Need to show more columns ?

1- download
2- download
3- download
4- download 
""",
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
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
    'certificate': '',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: