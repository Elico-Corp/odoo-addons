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
class account_account_type(osv.osv):
	_name    = "account.account.type"
	_inherit = "account.account.type"

	_columns = {
        'level1': fields.many2one
    		(
		'res.report.attribute',
		'Level 1',
#			required=True,
		help="First level account category (based on the five standard IFRS/US-GAAP account types). Those categories are used in multi-company IFRS reports. N/A if not appliable"
		),
        'level2': fields.many2one
    		(
		'res.report.attribute',
		'Level 2',
#			required=True,
		help="Second level account category (based on IFRS). Those categories are used for totals in multi-company IFRS reports. N/A if not appliable"
		),
        'sequence': fields.integer
		(
		'Sequence', 
		help="Gives the sequence order when displaying a list of account types."
		),
	'current': fields.boolean
		(
		'Current',
		required=True,
		help="Select whether this account is current or long-term (aka non-current). A 'current' account means it applies to the current fiscal year."
		),
	'operating': fields.boolean
		(
		'Operating', 
		required=True, 
		help="Select whether this account is operating or non-operating. An 'operating' account means it applies to core operations of the company.  Otherwise, 'non-operating' means it applies to non-core operations."
		),
	'company_id': fields.many2one
		(
		'res.company', 
		'Company', 
		required=True
		),
	}

	_defaults = {
	'current':    lambda *a: True,
	'operating':  lambda *a: True,
#	'level1':     lambda self, cr, uid, context : self.pool.get('res.report.attribute').search(cr, uid, [('code', '=', 'na_l1')])[0],
#	'level2':     lambda self, cr, uid, context : self.pool.get('res.report.attribute').search(cr, uid, [('code', '=', 'na_l2')])[0],
        'sequence':   lambda *a: 5,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
	}

account_account_type()

