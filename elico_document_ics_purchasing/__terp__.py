# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (c) 2010 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <elicoidal@hotmail.com>
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
    'name': 'Support for iCal based on Document Management System',
    'version': '1.0',
    'category': 'Generic Modules/Others',
    'description': """Allows to synchronise calendars with others applications.""",
    'author': 'Elico Corp',
    'website': '',
    'depends': ['document', 'crm_configuration_purchasing'],
    'init_xml': ['document_data.xml'],
    'update_xml': ['document_view.xml', 'elico_document_ics_purchasing_config_wizard.xml'],
    'demo_xml': ['document_demo.xml'],
    'installable': True,
    'active': False,
    'certificate': '',
}
