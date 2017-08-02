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

from report import report_sxw
import time


class financial_statements_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(financial_statements_report, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time':			time,
			'get_report_header':	self.get_report_header,
			'get_cumul':		self.get_cumul,
			'get_lines':            self.get_lines,
                })
		self.context = context

	def _get_account_period_balance(self, cr, uid, qry_journal='', context=None):

		account_id = context['account_id']
		company_id  = context['company_id']
		query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
		query = query + qry_journal 

		cr.execute("SELECT sum(debit-credit) "\
			"FROM account_move_line l "\
			"WHERE l.account_id = %s AND l.company_id = %s  AND "+query, (account_id, company_id) )
		return cr.fetchone()[0] or 0.0

	def _get_account_period_budget(self, cr, uid, context=None):
#future use	
		return 0.0
	
	def _compare_periods(self, period1, period2):
		res=9999.99
		if period2!=0:
			res=(period1/period2-1)*100
		return res
	def get_report_header(self, form):
		result = []
		clause=')'.join(str('('.join(str(form['periods1']).split('['))).split(']'))
		self.cr.execute('SELECT name FROM "account_period" WHERE id in '+clause+' ORDER BY name', ) 
		periods1=''
		for x in self.cr.fetchall():
			periods1= periods1 +', '*(periods1!='')+ str(x[0])	
		periods2 =    []
		if form['periods2']!=[]:
			clause=')'.join(str('('.join(str(form['periods2']).split('['))).split(']'))
			self.cr.execute('SELECT name FROM "account_period" WHERE id in '+clause+' ORDER BY name', ) 
			periods2=''
			for x in self.cr.fetchall():
				periods2= periods2 +', '*(periods2!='')+ str(x[0])	
		
		company_name =     self.pool.get('res.company').browse(self.cr, self.uid, form['company_id']).name
		company_curr =     self.pool.get('res.company').browse(self.cr, self.uid, form['company_id']).currency_id.name
		report_name=       'Accounts report'
		report_details =   'Custom'
		details =          ''
		if form['report_type']=='ISRep': report_name='Income Statement'
		if form['report_type']=='BSRep': report_name='Statement of Financial Position'
		if form['report_details']=='RepSum': report_details='Summary'
		if form['report_details']=='RepSim': report_details='Simple'
		if form['report_details']=='RepDet': report_details='Detailed'
		if report_details == 'Custom':
			details =''
			for field in ['field_1','field_2','field_3','field_4','field_5']:
				if form[field]:
					details = details + ', '*(details!='') + field + ': ' + str(form[field]) 
					details = details + ' (acc= '+ str(form['c_'+field]) + ')'

		res = {
			'periods1':    		 periods1,
			'periods2':    		 periods2,
			'hide_accounts':  	 form['hide_accounts'],
			'company_name':		 company_name,
			'company_curr':		 company_curr,
			'report_name':       report_name,
			'report_details':    report_details,
			'details':           details
		}
		
		result.append(res)
		return result

	def get_cumul(self,form,attribute=''):
		res = False
		if attribute=='':
			return res
		else:
			for f in ['field_1','field_2','field_3','field_4','field_5']:
				if form[f]==attribute and form['c_'+f]: 
					res = True
					break
			return res

	
	def get_lines(self, form):
		
		# Building the filter SQL sentence according to the type of report and multi-company constraint
		qry_journal=''
		if form['report_type']=='ISRep':
			self.cr.execute('select id from account_journal where centralisation=False', )
			ids = [x[0] for x in self.cr.fetchall()]
			ids_as_sql_list   = ')'.join(str('('.join(str(ids     ).split('['))).split(']'))
			qry_journal = ' AND journal_id in '+ids_as_sql_list

			clause=')'.join(str('('.join(str(['expenses','income']).split('['))).split(']'))
			self.cr.execute('select id from res_report_attribute where code in '+clause, )
			ids = [x[0] for x in self.cr.fetchall()]
			ids_as_sql_list   = ')'.join(str('('.join(str(ids     ).split('['))).split(']'))

			strfilter = ' account_account.company_id = %s and account_account_type.level1 in '+ids_as_sql_list
			if form['report_details']!='RepCus':
				form['field_1']='level2'
				form['c_field_1']= True
				if form['report_details']=='RepSim': 
					form['field_2']='user_type'
					form['c_field_2']= False
				if form['report_details']=='RepDet': #not needed
					form['field_2']='user_type'
					form['c_field_2']= False

		if form['report_type']=='BSRep':
			clause=')'.join(str('('.join(str(['assets',	'liabilities','equities',]).split('['))).split(']'))
			self.cr.execute('select id from res_report_attribute where code in '+clause, )
			ids = [x[0] for x in self.cr.fetchall()]
			ids_as_sql_list   = ')'.join(str('('.join(str(ids     ).split('['))).split(']'))
			strfilter = ' account_account.company_id = %s and account_account_type.level1 in '+ids_as_sql_list

			if form['report_details']!='RepCus':
				form['field_1']='level1'
				form['c_field_1']= False
				if form['report_details']=='RepSim': 
					form['field_2']='level2'
					form['c_field_2']= False
				if form['report_details']=='RepDet': 
					form['field_2']='level2'
					form['c_field_2']= False
					form['field_3']='user_type'
					form['c_field_3']= False
		result = []
		level = 1
		fiscalyear1=form['fiscalyear1']
		fiscalyear2=form['fiscalyear2']
		ctx = self.context.copy()
		periods1 = form['periods1']
		periods2 = form['periods2']
		compared = periods2 !=[]
		ctx['periods'] = periods1 
		ctx['fiscalyear'] = fiscalyear1

		company  = form['company_id'] 
		ctx['company_id'] = company 

		#Building the order sequence SQL sentence
		strorderby=' account_account.code'
		for strfield in ['field_5','field_4','field_3','field_2','field_1']:
			strorderby =  ' tlevel1.sequence,'*(form[strfield]=='level1') +\
			              ' tlevel2.sequence,'*(form[strfield]=='level2') +\
			              ' account_account_type.sequence,'*(form[strfield]=='user_type') +\
			              ' account_account_type.current,'*(form[strfield]=='current') +\
			              ' account_account_type.operating,'*(form[strfield]=='operating') +\
			              strorderby
		strorderby= ' ORDER BY' + strorderby

		#SQL Statement to retrieve all account information in on line, order by the user's request for the report.
		strfilter = ' WHERE'+ strfilter
		strquery = \
		  'SELECT account_account.id, \
				tlevel1.name as level1, \
				tlevel2.name  as level2, \
				account_account_type.name, \
				account_account_type.current, \
				account_account_type.operating, \
				account_account_type.report_type, \
				account_account.parent_id, \
				account_account.type, \
				account_account.code, \
				account_account.name \
			FROM account_account INNER JOIN account_account_type \
			ON account_account_type.id = account_account.user_type \
			INNER JOIN \
			   (SELECT res_report_attribute.id, \
			           res_report_attribute.name, \
				  	   res_report_attribute.sequence \
			    FROM res_report_attribute \
				   ) as tlevel1 \
			ON tlevel1.id = account_account_type.level1 \
			INNER JOIN \
			   (SELECT res_report_attribute.id, \
				       res_report_attribute.name, \
				       res_report_attribute.sequence \
			    FROM res_report_attribute \
				   ) as tlevel2 \
			ON tlevel2.id = account_account_type.level2' \
			+ strfilter \
			+ strorderby

#0	account_account.id, \
#1	tlevel1.name, \
#2	tlevel2.name, \
#3	account_account_type.name, \
#4	account_account_type.current, \
#5	account_account_type.operating, \
#6	account_account_type.report_type, \
#7  Account_account.parent_id \
#8  Account_account.type \
#9  Account_account.code \
#10 Account_account.name \

		self.cr.execute(strquery, (str(company)))
		account_list = self.cr.fetchall()
		if account_list!=[]:
			#contains the result to be appended
			res = {
					'id':           -1,
					'total':        False,
					'type':         '',
					'code':         '',
					'name':         '',
					'level':        0.0,
					'period1':      0.0,
					'period2':      0.0,
					'budget':       0.0,
					'diff_1_2':		0.0,
					'diff_1_budg':	0.0,
					}
			#contains the totals to be appended
			totals = {
					'level1':       '',
					's1level1':      0.0,
					's2level1':      0.0,
					's3level1':      0.0,
					'level2':       '',
					's1level2':      0.0,
					's2level2':      0.0,
					's3level2':      0.0,
					'user_type':    '',
					's1user_type':   0.0,
					's2user_type':   0.0,
					's3user_type':   0.0,
					'current':      '',
					's1current':     0.0,
					's2current':     0.0,
					's3current':     0.0,
					'operating':    '',
					's1operating':   0.0,
					's2operating':   0.0,
					's3operating':   0.0,
						}
			#contains the flags for each level if a cumulative total is needed (mostly needed for gross profit report)
			c_totals = {
   					'level1':       self.get_cumul(form,'level1'),
					'level2':       self.get_cumul(form,'level2'),
					'user_type':    self.get_cumul(form,'user_type'),
					'current':      self.get_cumul(form,'current'),
					'operating':    self.get_cumul(form,'operating'),
					   }

			for account in account_list:
				#contains the total from previous calculation. We can test if the level total has changed.
				prev_totals= totals
				acc = self.pool.get('account.account').browse(self.cr, self.uid, account[0], ctx)
				ctx['account_id'] = account[0] 
				ctx['periods'] = periods1 
				ctx['fiscalyear'] = fiscalyear1
				#since v6, calculation sign is based on report_type field. 
				sign = 0
				sign=(account[6]=='asset') or (account[6] == 'liability' or account[6]=='income' or account[6] == 'expense')* (-1)
				bal_per1 = self._get_account_period_balance(self.cr, self.uid, qry_journal, ctx)*sign
				bal_budg = 0
				bal_per2 = 0 
				if compared:
					bal_budg = self._get_account_period_budget(self.cr, self.uid, ctx)*sign
					ctx['periods'] = periods2 
					ctx['fiscalyear'] = fiscalyear2 
					bal_per2 = self._get_account_period_balance(self.cr, self.uid, qry_journal, ctx)*sign

	
				#root of chart of account
				if account[9]== '0':
					continue
				totals = {
					'level1':       account[1],
					's1level1':      (totals['s1level1'])*(prev_totals['level1']== account[1] or c_totals['level1'])+bal_per1*(account[8]!='view'),
					's2level1':      (totals['s2level1'])*(prev_totals['level1']== account[1] or c_totals['level1'])+bal_per2*(account[8]!='view'),
					's3level1':      (totals['s3level1'])*(prev_totals['level1']== account[1] or c_totals['level1'])+bal_budg*(account[8]!='view'),
					'level2':       account[2], 
					's1level2':      (totals['s1level2'])*(prev_totals['level2']== account[2]or c_totals['level2'])+bal_per1*(account[8]!='view'),
					's2level2':      (totals['s2level2'])*(prev_totals['level2']== account[2]or c_totals['level2'])+bal_per2*(account[8]!='view'),
					's3level2':      (totals['s3level2'])*(prev_totals['level2']== account[2]or c_totals['level2'])+bal_budg*(account[8]!='view'),
					'user_type':    account[3], 
					's1user_type':   (totals['s1user_type'])*(prev_totals['user_type']== account[3]or c_totals['user_type'])+bal_per1*(account[8]!='view'), 
					's2user_type':   (totals['s2user_type'])*(prev_totals['user_type']== account[3]or c_totals['user_type'])+bal_per2*(account[8]!='view'), 
					's3user_type':   (totals['s3user_type'])*(prev_totals['user_type']== account[3]or c_totals['user_type'])+bal_budg*(account[8]!='view'), 
					'current':      account[4],
					's1current':     (totals['s1current'])*(prev_totals['current']== account[4]or c_totals['current'])+bal_per1*(account[8]!='view'),
					's2current':     (totals['s2current'])*(prev_totals['current']== account[4]or c_totals['current'])+bal_per2*(account[8]!='view'),
					's3current':     (totals['s3current'])*(prev_totals['current']== account[4]or c_totals['current'])+bal_budg*(account[8]!='view'),
					'operating':    account[5],
					's1operating':   (totals['s1operating'])*(prev_totals['operating']== account[5]or c_totals['operating'])+bal_per1*(account[8]!='view'),
					's2operating':   (totals['s2operating'])*(prev_totals['operating']== account[5]or c_totals['operating'])+bal_per2*(account[8]!='view'),
					's3operating':   (totals['s3operating'])*(prev_totals['operating']== account[5]or c_totals['operating'])+bal_budg*(account[8]!='view'),
					}
				#Building intermediates lines for the totals, according to user request
				if res['id']!=-1: #we do not need to check for the first time it goes into the loop (prev_res is obviously nill)
					i=5
					for strfield in [form['field_5'],form['field_4'],form['field_3'],form['field_2'],form['field_1']]:
						if strfield:
							if prev_totals[strfield]!= totals[strfield ]:
								res2 = {
									'id':          0,
									'total':       True,    
									'type':        str(i),
									'code':        ((i==1)*'Grand Total' or (i==2)*'Total' or (i==3)*'Sub-total' or	(i==4)*'Sub-Total' or (i==5)*'Sub-Total')
													+(strfield =='current')*' (Current)'+ (strfield == 'operating')*' (Operating)',
									'name':        str(prev_totals[strfield]),
									'level':       0,
									'period1':     prev_totals['s1'+strfield],
									'period2':     prev_totals['s2'+strfield],
									'budget':      prev_totals['s3'+strfield],
									'diff_1_2':    self._compare_periods(prev_totals['s1'+strfield],prev_totals['s2'+strfield]),
									'diff_1_budg': self._compare_periods(prev_totals['s1'+strfield],prev_totals['s3'+strfield]),
								}
								result.append(res2)			
						i -=1
				res['id']=0
				# if desired skip postable accounts with no activity (zero debit/credit and no child accounts)
				if form['skip_accts_no_activity'] and not (bal_per1 or bal_per2 or bal_budg) and not acc.child_id:
					continue
				if not form['hide_accounts']:
					#We add the result for the selected acccount
					if not (form['hide_view_accounts'] and account[8]=='view'):
						res = {
							'id':         account[0],
							'total':	  False,
							'type':       account[8],
							'code':       account[9],
							'name':       account[10],
							'level':      level,
							'period1':    bal_per1,
							'period2':    bal_per2,
							'budget':     bal_budg,
							'diff_1_2':	  self._compare_periods(bal_per1,bal_per2),
							'diff_1_budg':self._compare_periods(bal_per1,bal_budg),
						}
						#We adapt the level according to parent level
						if account[7] : 
							for r in result:
								if r['id'] == account[7]:
										res['level'] = r['level'] + 1
										break
						result.append(res)
			#We build the final total
			i=5
			for strfield in [form['field_5'],form['field_4'],form['field_3'],form['field_2'],form['field_1']]:
				if strfield:
					res2 = {
						'id':         0,    
						'total':      True,    
						'type':       str(i),
						'code':        ((i==1)*'Grand Total' or (i==2)*'Total' or (i==3)*'Sub-total' or	(i==4)*'Sub-Total' or (i==5)*'Sub-Total')
										+(strfield =='current')*' (Current)'+ (strfield == 'operating')*' (Operating)',
						'name':       str(totals[strfield]),
						'level':      0,
						'period1':    totals['s1'+strfield],
						'period2':    totals['s2'+strfield],
						'budget':     totals['s3'+strfield],
						'diff_1_2':	  self._compare_periods(totals['s1'+strfield],totals['s2'+strfield]),
						'diff_1_budg':self._compare_periods(totals['s1'+strfield],totals['s3'+strfield]),
					}
					result.append(res2)			
				i -=1

		return result
	
report_sxw.report_sxw('report.account_financial_statements.financial.statements.report', 
	'account.account', 
	'addons/account_financial_statements/report/financial_statements_report.rml', 
	parser=financial_statements_report, 
	header=False)
report_sxw.report_sxw('report.account_financial_statements.financial.statements.compared.report', 
	'account.account', 
	'addons/account_financial_statements/report/financial_statements_compared_report.rml', 
	parser=financial_statements_report, 
	header=False)
