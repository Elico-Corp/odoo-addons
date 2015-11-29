# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Chen Rong <chen.rong@elico-corp.com>
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
    'name': 'project git branch',
    'version': '0.1',
    'category': 'Category',
    'depends': [
        "project"
    ],
    'author': 'Elico-Corp,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        "project_view.xml",
    ],
    'installable': True,
    'application': False
}
