# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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


from osv import fields, osv
class res_report_attribute(osv.osv):
	_name    = "res.report.attribute"
	_description = "Reporting Attributes"
	_columns = {
		'type': fields.char
			( 
			'Attribute Type', 
			size=32, 
			required=True, 
			help="Attribute Type"
			),
		'code': fields.char
			( 
			'Attribute Code', 
			size=32, 
			required=True, 
			help="Attribute Code"
			),
		'name': fields.char
			( 
			'Attribute Name', 
			size=32, 
			required=True, 
			help="Attribute Name"
			),
		'sequence': fields.integer
			( 
			'Attribute Sequence', 
			required=True, 
			help="Attribute Sequence"
			),
		'company_id': fields.many2one
			(
			'res.company', 
			'Company', 
			required=True
			),
	}
	_defaults = {
		'type':       lambda *a: 'none',
		'code':       lambda *a: 'none',
		'name':       lambda *a: 'none',
		'sequence':   lambda *a: 5,
	        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
res_report_attribute()
