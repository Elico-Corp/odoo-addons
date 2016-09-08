# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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
{'name': 'Cron Watcher',
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
 'application': False}
