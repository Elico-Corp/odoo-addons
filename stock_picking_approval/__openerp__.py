#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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
    'name':'Stock picking approval step',
    'version':'1.0',
    'depends':["stock"],
	"author" : "Elico Corp",
    "description": """
    Add a group for picking approval during the stock "check availability" process. 
    """,
    'website': 'www.openerp.net.cn',
    'init_xml': [
    ],
    'update_xml': [
        'stock_picking_approval_view.xml',
        'stock_picking_approval_workflow.xml',
    ],
    'demo_xml': [
        
    ],
    'installable': True,
    'active': False,
}
