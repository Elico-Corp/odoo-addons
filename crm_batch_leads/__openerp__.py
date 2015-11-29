# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#    Author: LIN Yu <lin.yu@elico-corp.com>
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
    'name': 'CRM & Projects ACL',
    'version': '1.1',
    'category': 'Generic Modules/Others',
    'complexity': 'easy',
    'author': 'Elico Corp,Odoo Community Association (OCA)',
    'website': 'http://www.openerp.net.cn/',
    'depends': [
        'crm',
        'email_template',
    ],
    'data': ['wizard/batch_lead_view.xml', 'email_template.xml'],
    'installable': True,
    'active': False,
}
