# -*- coding: utf-8 -*-
#   2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Cron Watcher',
    'version': '0.1',
    'category': 'Tools',
    'depends': ['base', 'mail'],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'description': """
Sends notification to a group named "Cron Watcher" when a cron job has not run
for X minutes.

X can be defined in "Settings", "Scheduler Actions", "Cron Watcher",
"Technical Data", "Arguments"
    * 5 minutes = (5,)
    * 10 minutes = (10,)
    * etc...
""",
    'data': ['cron_data.xml'],
    'installable': True,
    'application': False
}
