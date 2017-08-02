# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2010 Eric CAUDAL. All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Supplier Relationship Management',
    'version': '1.0',
    'category': 'Generic Modules/CRM & SRM',
    'description': """
The Open ERP case and request tracker enables a group of
people to intelligently and efficiently manage tasks, issues,
and requests. It manages key tasks such as communication, 
identification, prioritization, assignment, resolution and notification.

This module provide screens like: jobs hiring process, leads, business
opportunities, fund raising tracking, support & helpdesk, calendar of
meetings, eso.

Specific module for purchasing activity: 
    - Create 2 new section types for purchasing activity: purchasing opportunities and purchasing leads.
    - Add specific fields for supplier relationship management: tags, website, fair name and collected material.
    - Add usefull searchable fields (note, tags)
    - alter the convert to partner button to create supplier and pass the added information into the partner.
    - call the document_ics_purchasing module accordingly, to create the requested calendars
    - Create a specific dashboard for purchasing
""",
    'author': 'Eric CAUDAL (dev@elico-corp.com)',
    'website': 'http://www.openerp.net.cn',
    'depends': ['crm_configuration','board_crm_configuration'],
    'init_xml': [
        'crm_configuration_wizard.xml',
        'crm_config_view.xml',
        'crm_lead_purchasing_view.xml',
        'crm_opportunity_purchasing_view.xml',
	'crm_case_purchasing_board_view.xml'
    ],
    'update_xml': ['security/ir.model.access.csv','crm_case_purchasing_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
