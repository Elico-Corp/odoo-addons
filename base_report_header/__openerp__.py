# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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
    'name': 'Add multiple headers for reporting',
    'version': '1.0',
    'category': 'Tools',
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn',
    'depends': ['base'],
    'description': """
===================
SUMMARY
===================
This extension to Base module simply adds multi-header capabilities for reporting
with a dedicated report header's table.
Initially this module aims at adding extra landscape headers for external documents 
(in base module, only 3 headers are available in the company definition: 
1 for external docs and 2 for internal), which is a problem if you have external reports
both in portrait and landscape mode. 

===================
HOW IT WORKS
===================
A specific table res_header stores the headers in rml format (same as
in the company definition). To be filled in Administration/Reporting/Reporting Headers.

This module gives an example of wrapping the function to use the specific table. 
_add_header(self, rml_dom, header='external')

Check the report example given in the module to see how to add _add_header() function to your own reports.
Once added, you will be able to create and use different header in the following function calls:
    report_sxw.report_sxw('report.name', 'model.name', 'path_to_rml/report.rml', 
    parser=parser_function, header='name_of_header)

On top of current headers ('internal', 'external' and 'internal landscape'), 
you can specify for 'header=' whatever header's name you created in the report header's table located in 
Administration/Reporting/Reporting Headers.

===================
RESTRICTION
===================
- 'internal', 'external' and 'internal landscape' are OpenERP reserved name
- You have to manually fill in the headers in the interface (2 default entries are added in the database though) 
(an ready-to-use header example is given in the file l10n_cn_report_header_example.xml)
===================
TODO
===================
- add multi-company capability
- generate default entries for the table res_header.
 
    """,
    'init_xml': [],
    'update_xml': [
        'base_report_header_view.xml',
        'base_report_header_data.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
