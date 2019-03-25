# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Mail Batch Read',
    'author': 'Elico Corp',
    'sequence': '119',
    'depends': ['mail'],
    'data': ['message_list.xml',
             'wizard/read_multiple_mails.xml',
             'security/ir.model.access.csv',
             'security/messages_access_rules.xml'],
    'application': False,
}
