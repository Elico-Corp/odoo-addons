# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-Present Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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

from osv import fields, osv
import report

class res_header(osv.osv):
    _name    = "res.header"
    _description = "Reporting headers"
    _columns = {
        'name': fields.char
            ( 
            'Header''s Name', 
            size=128, 
            required=True, 
            help="Header's Name (except 'internal', 'internal landscape' and 'external')"
            ),
        'rml_header': fields.text
            ( 
            'Header''s content', 
            required=True, 
            help="RML header's content"
            ),
        'internal': fields.boolean
            ( 
            'Internal', 
            required=True, 
            help="Header for internal use only"
            ),
    }
    _defaults = {
        'internal':   lambda *a: False,
    }
    
res_header()
