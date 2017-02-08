# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Mail Batch Read',
    'description': '''
    In the same view as Inbox, add a "list" view button. When switching to
    list view, display the following info:
    - Date: date
    - From: partner_ids
    - Subject: subject
    - Body (only the begginning)
    - When the user checks one or several emails, add an option in the drop
    down menu to mark them all as read.
    ''',
    'author': 'Elico Corp',
    'sequence': '119',
    'license': '',
    'support': '',
    'depends': ['mail'],
    'data': ['message_list.xml',
             'wizard/read_multiple_mails.xml',
             'security/ir.model.access.csv',
             'security/messages_access_rules.xml'],
    'application': False,
}
