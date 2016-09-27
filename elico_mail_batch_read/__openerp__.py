# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Rona Lin <rona.lin@elico-corp.com>
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
    'name': 'Mail Batch Read',
    'description': '''
    In the same view as Inbox, add a "list" view button. When switching to list
    view, display the following info:
    - Date: date
    - From: partner_ids
    - Subject: subject
    - Body (only the begginning)
    - When the user checks one or several emails, add an option in the drop down
    menu to mark them all as read.
    ''',
    'author': 'Elico corp',
    'sequence': '119',
    'depends': ['mail'],
    'data': ['message_list.xml',
             'wizard/read_multiple_mails.xml',
             'security/ir.model.access.csv',
             'security/messages_access_rules.xml'],
    'application': False,
}