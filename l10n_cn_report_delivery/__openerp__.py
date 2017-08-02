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
    'name': 'Chinese-English delivery notes/中英文送货单',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """
Implement the following documents in English and Chinese language:

- Delivery notes

Please note that you will have to:

1. install module base_report_header
2. create an entry in Administration/Reporting/Reporting Header called 'external landscape' 
3. fill rml header (you can copy the one in the field header/footer from the company) 
This is necessary for the moment to be able to have in OpenERP reports in landscape and portrait mode
Check file l10n_cn_report_header_example.xml for header example you can copy directly

    """,
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn',
    'images' : ['images/shipping.png'],
    'complexity': "normal",
    'depends': ['base_report_header', 'delivery'],
    'init_xml': [],
    'update_xml': [
		'l10n_cn_report_view.xml'
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
