##############################################################################
#
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import pooler
from tools.translate import _
import datetime
from osv import fields, osv
from mx.DateTime import *

class year_end_process_period_close(osv.osv_memory):
	"""
	For Year End Process Closing Period Wizard 
	"""
	_name = "year.end.process.period.close"
	_description = "Year End Process Closing Period Wizard"
	_columns = {
		'company_id': fields.many2one(
			'res.company',
			'Company', 
		    help='Company for which to close the period(s).', 
			required=True
			), 
		'fiscalyear': fields.many2one(
			'account.fiscalyear',
			'Fiscal year', 
			help='Fiscal Year containing the period(s) to be closed.', 
			required=True
			),
		'periods': fields.many2many(
			'account.period',
			'account_period_rel',
			'period_id',
			'periods',
			'Period(s) to be closed', 
			help= 'Periods to be closed for the selected fiscal year and company.',
			required=True
			),
		'net_income_acct_id': fields.many2one(
			'account.account', 
			'Retained Earnings Account', 
			help='Current "retained earnings" Account. Preferably use the same account for all period closing processes within a fiscal year. If no account is selected, the wizard only closes periods and 				journals for the selected periods.'
			),
		'report_journal': fields.many2one(
			'account.journal',
			'Closing Entries Journal',
			help= 'Select a centralized journal to record the closing entries.', 
			required=True
			),
		'report_name':fields.char(
			'Journal Entries name', 
			size=64, 
		    help='Description for the Journal Entries.', 
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
		'report_name':'Closing Period Process Entry',
		'fiscalyear':_get_default_fiscalyear,
		'company_id':_get_default_company_id,
		}

	def close_period(self, cr, uid, ids, context=None):
		def _get_account_period_total(self, cr, uid, data, context=None):

			# call: _get_account_period_total(self, cr, uid, data, context={'fieldname':'debit', 'account_id':account_id, 'period_id':period_id})
			fieldname  = context['fieldname']
			account_id = context['account_id']
			period_id  = context['period_id']
			query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
			cr.execute("SELECT sum("+fieldname+") "\
				"FROM account_move_line l "\
				"WHERE l.account_id = %s AND l.period_id = %s  AND "+query, (account_id, period_id) ) 
			return cr.fetchone()[0] or 0.0

		if context is None:
			context = {}
		data={}
		data['form']=self.read(cr, uid, ids, ['sure'])[0]
		if not data['form']['sure']:
			raise osv.except_osv('UserError', 'Process canceled, please check that you have a data backup and tick the confirmation box !')

		data['form']=self.read(cr, uid, ids, ['company_id', 'fiscalyear', 'periods', 'net_income_acct_id','report_journal','report_name'])[0]
		pool = pooler.get_pool(cr.dbname)
		self.pool = pool
		company= 		data['form']['company_id']
		net_account = 	data['form']['net_income_acct_id']
		report_journal=	data['form']['report_journal']
		report_name = 	data['form']['report_name']

		if net_account:
			for period in data['form']['periods']:
				created_move = False
				jp_ids = self.pool.get('account.journal.period').search(cr, uid, [('period_id', '=', period)]) 
				if jp_ids:
					# In principle this checking step is not necessary
					# get state for first journal period record for this period (all journal period records should be same)
					journal_period_state = self.pool.get('account.journal.period').read(cr, uid, jp_ids, ['state'])[0]['state']
					p_ids = self.pool.get('account.period').search(cr, uid, [('id', '=', period)])
					# get the state for the first account period record for this period (all account period records should be same)
					period_state = self.pool.get('account.period').read(cr, uid, p_ids, ['state'])[0]['state']
					if journal_period_state == 'done' and period_state == 'done':
						continue
					name = report_name+' ('+self.pool.get('account.period').read(cr, uid, p_ids, ['name'])[0]['name']+')'

					for accttype in ['income', 'expenses']:
						query = 'SELECT id FROM "res_report_attribute" WHERE type=%s and code = %s and company_id=%s'
						cr.execute(query, ('level1',accttype, company,))
						accttype_id = cr.fetchall()
						if not accttype_id:
							raise osv.except_osv(_('Error !'), _(
							'Closing process is based on the level 1 attribute set for account_account_type (either "income" or "expenses"). \
							Those attributes are missing in table "res_report_attribute" ("account report attributes" Form).'))

						#We get first the related account_type ids corresponding with the income/expenses classification
						sub_query = 'select id from "account_account_type" where level1 = %s and company_id = %s order by code' 
						query = 'select id from "account_account" where user_type in ('+sub_query+') and active order by code' 
						cr.execute(query, (accttype_id[0], company,))
						ids = map(lambda x: x[0], cr.fetchall())

						if not ids:
							continue
						for account in pool.get('account.account').browse(cr, uid, ids):
							if account.type == 'view':
								continue
							# BY BALANCE THAT IS ATTRIBUTABLE TO PERIOD TRANSACTIONS AND NOT BY TOTAL ACCOUNT BALANCE
							credit_period_balance = _get_account_period_total(self, cr, uid, data, context={'fieldname':'credit', 'account_id':account.id, 'period_id':period})
							debit_period_balance = _get_account_period_total(self, cr, uid, data, context={'fieldname':'debit', 'account_id':account.id, 'period_id':period})
							account_period_balance = credit_period_balance - debit_period_balance

							if abs(account_period_balance) < 0.0001:
								continue

							# create move header
							if not(created_move):
								move_id = pool.get('account.move').create(cr, uid, {
									'name': name,
									'journal_id': report_journal,
									'state': 'draft',
									'period_id': period,
									'ref': '',
									'company_id':company,
								}, {'journal_id': report_journal, 'period_id':period})
								created_move=True

							# create move_lines
							# income:  increase (credit) the net income summary account by account balance
							# expense: decrease (debit)  the net income summary account by account balance
							# we have to create separate lines: 1 for debit, 1 for credit to avoid check 
							# constraints in database that says at least debit or credit must be 0.
							if credit_period_balance >0.0001:
								pool.get('account.move.line').create(cr, uid, {
									'debit':        0.00,
									'credit':	credit_period_balance,
									'name':		name,
									'date':		now().date,
									'move_id':	move_id,
									'journal_id':	report_journal,
									'period_id':	period,
									'account_id':	net_account,
									'company_id':	company,
								}, {'journal_id':   report_journal, 'period_id':period})
								pool.get('account.move.line').create(cr, uid, {
									'debit':        credit_period_balance,
									'credit':       0.00,
									'name':         name,
									'date':         now().date,
									'move_id':      move_id,
									'journal_id':   report_journal,
									'period_id':    period,
									'account_id':   account.id,
									'company_id':   company,
								}, {'journal_id':   report_journal, 'period_id':period})

							if debit_period_balance >0.0001:
								pool.get('account.move.line').create(cr, uid, {
									'debit':	debit_period_balance,
									'credit':	0.00,
									'name':		name,
									'date':		now().date,
									'move_id':	move_id,
									'journal_id':	report_journal,
									'period_id':	period,
									'account_id':	net_account,
									'company_id':	company,
								}, {'journal_id':   report_journal, 'period_id':period})
								pool.get('account.move.line').create(cr, uid, {
									'debit':        0.00,
									'credit':       debit_period_balance,
									'name':         name,
									'date':         now().date,
									'move_id':      move_id,
									'journal_id':   report_journal,
									'period_id':    period,
									'account_id':   account.id,
									'company_id':   company,
								}, {'journal_id':   report_journal, 'period_id':period})

					#We validate the centralized journal
					obj_move = self.pool.get('account.move')
					ids_move = obj_move.search(cr, uid, [('state','=','draft'),('journal_id','=',report_journal),('period_id','=',period)])
					if ids_move:
						obj_move.button_validate(cr, uid, ids_move, context=context)

		# close period (mark it 'done')
		query_periods_list= ')'.join(str('('.join(str(data['form']['periods']).split('['))).split(']'))
		cr.execute('UPDATE account_journal_period ' \
				'SET state = %s ' \
				'WHERE period_id IN '+query_periods_list,
				('done',))
		cr.execute('UPDATE account_period SET state = %s ' \
				'WHERE id IN '+query_periods_list,
				('done',))
		return {}
year_end_process_period_close()

