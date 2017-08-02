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
import time
import pooler
from tools.translate import _

class year_end_process_period_open(osv.osv_memory):
	"""
	For Year End Process Opening Period Wizard 
	"""
	_name = "year.end.process.period.open"
	_description = "Year End Process Opening Period Wizard"
	_columns = {
	'company_id': fields.many2one(
		'res.company',
		'Company', 
			help='Company for which to close the period(s).', 
		required=True
		), 
	'ofy_id': fields.many2one(
		'account.fiscalyear',
		'Closing Fiscal year', 
		help='Fiscal Year from which will be transfer the entries.', 
		required=True
		),
	'journal_id': fields.many2one(
		'account.journal',
		'Opening Entries Journal',
		help= 'Select a centralized journal to record the opening entries.', 
		required=True
		),
	'period_id': fields.many2one(
		'account.period',
		'Opening Entries Period', 
		required=True, 
		help='Period that will contain all the opening entries in the new fiscal year (eg: 00/20xx).', 
		),
	'nfy_id': fields.many2one(
		'account.fiscalyear',
		'Opening fiscal year', 
		help='Fiscal Year to which will be transfer the entries.', 
		required=True
		),
	'report_name':fields.char(
		'Journal entries name', 
		size=64, 
			help='Description for the Journal Entries.', 
		required=True
		),
	'writeoff_acc_id': fields.many2one(
		'account.account',
		'Write-off Account',
		required=True
		),
	'writeoff_journal_id': fields.many2one(
		'account.journal',
		'Write-off Journal',
		help= 'Select a journal to record the reconcile entries.', 
		required=True
		),
	'writeoff_period_id': fields.many2one(
		'account.period',
		'Write-off Period', 
		required=True, 
		help='Period to record the reconcile entries.', 
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
		'report_name':'Opening Period Process Entry',
		'nfy_id':_get_default_fiscalyear,
		'company_id':_get_default_company_id,
	}

	def open_period(self, cr, uid, ids, data, context=None):
		def _test_input(cr, uid, data, pool, context):
			"""Check if the fiscal year and the account and the wizard form inputs are valids"""
			##validate the fy
			fy = pool.get('account.fiscalyear').browse(cr, uid, data['form']['ofy_id'])
			fy2 = pool.get('account.fiscalyear').browse(cr, uid, data['form']['nfy_id'])
			## closing date
			date_stopfy = time.strptime(fy.date_stop, '%Y-%m-%d')
			## opening date
			date_startfy2 = time.strptime(fy2.date_start, '%Y-%m-%d')
	
			if date_stopfy > date_startfy2 :
				raise wizard.except_wizard('UserError',
					    'The Fiscal Year must be successive') 
			## we get all the fiscal year start date that are not in the selecte one
			cr.execute('select name, date_start, state from account_fiscalyear where \
				id not in(%s,%s)',
				(fy.id, fy2.id))
			res = cr.dictfetchall()
			if res :
			## we test if there is a fiscal year open between 
				for fy_to_test in res :
					date_to_test = time.strptime(fy_to_test['date_start'], '%Y-%m-%d')
					if date_to_test > date_stopfy \
					and date_to_test < date_startfy2 :
					    raise osv.except_osv('UserError',
					    'There is a fiscal year between the ones you want to close : '\
					    +fy_to_test['name']) 
			## we test if all the previous fiscal year are closed
				for fy_to_test in res :
					date_to_test = time.strptime(fy_to_test['date_start'], '%Y-%m-%d')
					if date_to_test < date_stopfy \
					and fy_to_test['state'] != 'done' :
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

		data['form']=self.read(cr, uid, ids, ['company_id', 'ofy_id', 'journal_id', 'period_id', 'nfy_id','report_name', 'writeoff_acc_id','writeoff_journal_id', 'writeoff_period_id'])[0]

		pool = pooler.get_pool(cr.dbname)
		_test_input(cr, uid, data, pool, context)

		company = data['form']['company_id']
		nfy_id = data['form']['nfy_id']
		ofy_id = data['form']['ofy_id']
		period = pool.get('account.period').browse(cr, uid, data['form']['period_id'], context=context)
		new_journal = pool.get('account.journal').browse(cr, uid, data['form']['journal_id'], context=context)

		ofy = pool.get('account.fiscalyear').browse(cr, uid, ofy_id, context=context)
		ofy_period_ids = pool.get('account.period').search(cr, uid, [('fiscalyear_id', '=', ofy_id)])
		ofy_period_set = ','.join(map(str, ofy_period_ids))

		ofy = pool.get('account.fiscalyear').browse(cr, uid, nfy_id, context=context)
		nfy_periods_ids = pool.get('account.period').search(cr, uid, [('fiscalyear_id', '=', nfy_id)])
		nfy_period_set = ','.join(map(str, nfy_periods_ids))


		if not new_journal.default_credit_account_id or not new_journal.default_debit_account_id:
			raise osv.except_osv(_('UserError'),
					_('The journal must have default credit and debit account'))
		if not new_journal.centralisation:
			raise osv.except_osv(_('UserError'),
					_('The journal must have centralised counterpart'))

		move_ids = pool.get('account.move.line').search(cr, uid, 
		[('journal_id','=',new_journal.id),('period_id.fiscalyear_id','=',ofy.id)])
		if move_ids:
			raise osv.except_osv(_('UserError'),
					_('The opening journal must not have any entry in the new fiscal year !'))

		query_line = pool.get('account.move.line')._query_get(cr, uid,
				obj='account_move_line', context={'fiscalyear': ofy_id})
		cr.execute('select id from account_account WHERE active and company_id=%s',
			(company,)) 

		ids = map(lambda x: x[0], cr.fetchall())
		#print 'ids'+str(ids)
		for account in pool.get('account.account').browse(cr, uid, ids,context={'fiscalyear': ofy_id}):
			accnt_type_data = account.user_type
			#print 'account/account_type/balance/closing'+str(account) + str(accnt_type_data)+str(account.balance)+str(accnt_type_data.close_method)
			if not accnt_type_data:
				continue
			if accnt_type_data.close_method=='none' or account.type == 'view':
				continue
			if accnt_type_data.close_method=='balance':
				if abs(account.balance)>0.0001:
					pool.get('account.move.line').create(cr, uid, {
						'debit': account.balance>0 and account.balance,
						'credit': account.balance<0 and -account.balance,
						'name': data['form']['report_name'],
						'date': period.date_start,
						'journal_id': new_journal.id,
						'period_id': period.id,
						'account_id': account.id,
						'company_id': company, 
					}, {'journal_id': new_journal.id, 'period_id':period.id})
			if accnt_type_data.close_method == 'unreconciled':
				offset = 0
				limit = 100
				while True:
					cr.execute('SELECT id, name, quantity, debit, credit, account_id, ref, ' \
								'amount_currency, currency_id, blocked, partner_id, ' \
								'date_maturity, date_created ' \
							'FROM account_move_line ' \
							'WHERE account_id = %s ' \
								'AND ' + query_line + ' ' \
								'AND reconcile_id is NULL ' \
							'ORDER BY id ' \
							'LIMIT %s OFFSET %s', (account.id, limit, offset))
					result = cr.dictfetchall()
					#print "result"+str(result)
					if not result:
						break
					for move in result:
						move.pop('id')
						move.update({
							'date': period.date_start,
							'journal_id': new_journal.id,
							'period_id': period.id,
						})
						pool.get('account.move.line').create(cr, uid, move, {
							'journal_id': new_journal.id,
							'period_id': period.id,
							'company_id': company, 
							})
						#print 'move après='+str(move)
						#print" "
					offset += limit

				#We have also to consider all move_lines that were reconciled 
				#on another fiscal year, and report them too
				offset = 0
				limit = 100

				while True:
					#TODO: this query could be improved in order to work if there is more than 2 open FY
					# a.period_id IN ('+fy2_period_set+') is the problematic clause
					cr.execute('SELECT b.id, b.name, b.quantity, b.debit, b.credit, b.account_id, b.ref, ' \
								'b.amount_currency, b.currency_id, b.blocked, b.partner_id, ' \
								'b.date_maturity, b.date_created ' \
							'FROM account_move_line a, account_move_line b ' \
							'WHERE b.account_id = %s ' \
								'AND b.reconcile_id is NOT NULL ' \
								'AND a.reconcile_id = b.reconcile_id ' \
								'AND b.period_id IN ('+ofy_period_set+') ' \
								'AND a.period_id IN ('+nfy_period_set+') ' \
							'ORDER BY id ' \
							'LIMIT %s OFFSET %s', (account.id, limit, offset))
					result = cr.dictfetchall()
					if not result:
						break
					for move in result:
						move.pop('id')
						move.update({
							'date': period.date_start,
							'journal_id': new_journal.id,
							'period_id': period.id,
						})
						pool.get('account.move.line').create(cr, uid, move, {
							'journal_id': new_journal.id,
							'period_id': period.id,
							'company_id': company, 
							})
					offset += limit
			if accnt_type_data.close_method=='detail':
				offset = 0
				limit = 100
				while True:
					cr.execute('SELECT id, name, quantity, debit, credit, account_id, ref, ' \
								'amount_currency, currency_id, blocked, partner_id, ' \
								'date_maturity, date_created ' \
							'FROM account_move_line ' \
							'WHERE account_id = %s ' \
								'AND ' + query_line + ' ' \
							'ORDER BY id ' \
							'LIMIT %s OFFSET %s', (account.id, limit, offset))
		
					result = cr.dictfetchall()
					if not result:
						break
					for move in result:
						move.pop('id')
						move.update({
							'date': period.date_start,
							'journal_id': new_journal.id,
							'period_id': period.id,
						})
						pool.get('account.move.line').create(cr, uid, move)
					offset += limit
			# End of account loop

		#We validate the centralized journal
		obj_move = pool.get('account.move')
		ids_move = obj_move.search(cr, uid, [('state','=','draft'),('journal_id','=',new_journal.id),('period_id','=',period.id)])
		if ids_move:
			obj_move.button_validate(cr, uid, ids_move, context=context)

		#We reconcile the entries
		ids = pool.get('account.move.line').search(cr, uid, [('journal_id','=',new_journal.id),
			('period_id.fiscalyear_id','=',ofy.id)]) 
		context['fy_closing'] = True
		if ids:
			pool.get('account.move.line').reconcile(cr, uid, ids, 'auto',data['form']['writeoff_acc_id'], data['form']['writeoff_period_id'],data['form']['writeoff_journal_id'],context=context)

		#we create the new journal corresponding to new period
		new_period = data['form']['period_id']
		ids = pool.get('account.journal.period').search(cr, uid, [('journal_id','=',new_journal.id),
			('period_id','=',new_period)])
		if not ids:
			ids = [pool.get('account.journal.period').create(cr, uid, {
				   'name': (new_journal.name or '')+':'+(period.code or ''),
				   'journal_id': new_journal.id,
				   'period_id': period.id,
				   'company_id': company, 
			   })]
		cr.execute('UPDATE account_fiscalyear ' \
					'SET end_journal_period_id = %s ' \
					'WHERE id = %s', (ids[0], ofy.id))

		return {}
year_end_process_period_open()
