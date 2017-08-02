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
import pooler
from tools.translate import _
from osv import fields, osv
import time

class year_end_process_fiscalyear_close(osv.osv_memory):
	"""
	For Year End Process Closing Fiscal Year Wizard 
	"""
	_name = "year.end.process.fiscalyear.close"
	_description = "Year End Process Closing Fiscal Year Wizard"
	_columns = {
	'company_id': fields.many2one(
		'res.company',
		'Company', 
			help='Company for which to close the Fiscal Year.', 
		required=True
		), 
	'fy_id': fields.many2one(
		'account.fiscalyear',
		'Fiscal year to close', 
		help='Fiscal Year to be Closed.', 
		required=True
		),
	'sure': fields.boolean(
		'Check this box to confirm', 
		),
	}
	def _get_default_fiscalyear(self, cr, uid, context):
		fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
		return fiscalyear_obj.find(cr, uid)

	def _get_default_company_id(self, cr, uid, context):
		user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
		return user.company_id.id

	_defaults={
		'fy_id':_get_default_fiscalyear,
		'company_id':_get_default_company_id,
	}

	def close_fiscalyear(self, cr, uid, ids, context):
		def _test_input(cr, uid, data, pool, context):
			"""Check if the fiscal year and the account and the wizard form inputs are valids"""
			##validate the fy
			fy = pool.get('account.fiscalyear').browse(cr, uid, data['form']['fy_id'])
			date_stopfy = time.strptime(fy.date_stop, '%Y-%m-%d')
	
			## we get all the fiscal year start date that are not in the selecte one
			cr.execute('select name, date_start, state from account_fiscalyear where \
				id not in(%s)',	str(fy.id))
			res = cr.dictfetchall()
			print "res="+str(res)
			if res :
			## we test if all the previous fiscal year are closed
				for fy_to_test in res :
					date_to_test = time.strptime(fy_to_test['date_start'], '%Y-%m-%d')
					if date_to_test < date_stopfy and fy_to_test['state'] != 'done' :
					    raise osv.except_osv('UserError',
					    'There can not be an unclosed fiscal year before the one you want to open : '\
					    +fy_to_test['name']) 
			return True  
		if context is None:
			context = {}
		data={}
		data['form']=self.read(cr, uid, ids, ['sure'])[0]
		if not data['form']['sure']:
			raise osv.except_osv('UserError', 'Process canceled, please check that you have a data backup and tick the confirmation box !')

		data['form']=self.read(cr, uid, ids, ['company_id', 'fy_id'])[0]
		pool = pooler.get_pool(cr.dbname)
		_test_input(cr, uid, data, pool, context)

		fy_id = 	data['form']['fy_id']
		company = 	data['form']['company_id']

		cr.execute('UPDATE account_journal_period ' \
				'SET state = %s ' \
				'WHERE period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = %s and company_id = %s)',
				('done', fy_id, company))
		cr.execute('UPDATE account_period SET state = %s ' \
				'WHERE fiscalyear_id = %s  and company_id= %s', ('done', fy_id, company))
		cr.execute('UPDATE account_fiscalyear ' \
				'SET state = %s WHERE id = %s and company_id= %s', ('done', fy_id, company))
		return {}

year_end_process_fiscalyear_close()
