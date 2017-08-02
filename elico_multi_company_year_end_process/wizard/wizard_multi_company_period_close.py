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
import wizard
import pooler
from tools.translate import _
import datetime
import osv
from mx.DateTime import *

_transaction_form = '''<?xml version="1.0"?>
<form string="Multi-Company Closing Period Wizard">
    <separator string="Select Company and Fiscal Year" colspan="4"/>
   	<field name="company_id"/>  
	<field name="fiscalyear"/>

    <separator string="Detailed periods to be closed" colspan="4"/>
	<field name="periods" colspan="4"/>
	
    <separator string="Details" colspan="4"/>
	<field name="net_income_acct_id" colspan="4"/>
	<field name="report_journal" colspan="4"/>
	<field name="report_name" colspan="4"/>
	
    <separator string="Are you sure you want to create entries?" colspan="4"/>
	<field name="sure"/>

</form>'''

_transaction_fields = {
	'company_id': {
		'string':'Company', 
		'type':'many2one', 
		'relation': 'res.company',
        'help': 'Company for which to close the fiscal year.', 
		'required':True
		}, 
	'fiscalyear': {
		'string': 'Fiscal year', 
		'type': 'many2one', 
		'relation': 'account.fiscalyear', 
        'domain':"[('state','=','draft'),('company_id','=',company_id)]",
		'help': 'Fiscal Year containing the Period(s) of interest.', 
		'required': True
		},
	'periods': {
		'string': 'Periods', 
		'type': 'many2many', 
		'relation': 'account.period', 
        'domain':"[('fiscalyear_id','=',fiscalyear),('company_id','=',company_id)]",
		'help': 'Detailed periods of the fiscal year to close.',
        'required': True
		},
	'net_income_acct_id': {
		'string': 'Net Income Account', 
		'type': 'many2one', 
		'relation': 'account.account', 
        'domain': "[('company_id','=',company_id)]", 
		'help': 'Net Income Account(usually: Net Income - 200x). Always use the same account for all period closes within a fiscal year. If no account is selected, the wizard only closes selected periods and journals for the selected periods'
		},
	'report_journal': {
		'string':'Closing Entries Journal',
		'type':'many2one', 
		'relation': 'account.journal', 
        'domain':"[('company_id','=',company_id)]",
		'help': 'Select a Closing Journal or a Journal to record the closing entries.', 
		'required':True
		},
	'report_name':{
		'string':'Closing Period Process Entry', 
		'type':'char', 
		'size': 64, 
        'help': 'Default description of the accounting entries.', 
		'required':True},
	'sure': {
		'string':'Check this box (Backup recommended)', 
		'type':'boolean'
		},
}


def _get_account_period_total(self, cr, uid, data, context={}):

    # call: _get_account_period_total(self, cr, uid, data, context={'fieldname':'debit', 'account_id':account_id, 'period_id':period_id})
    fieldname  = context['fieldname']
    account_id = context['account_id']
    period_id  = context['period_id']
    query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
    cr.execute("SELECT sum("+fieldname+") "\
    	"FROM account_move_line l "\
    	"WHERE l.account_id = %s AND l.period_id = %s  AND "+query, (account_id, period_id) ) 
    return cr.fetchone()[0] or 0.0

def _data_load(self, cr, uid, data, context):
    data['form']['report_name'] = _('Closing Period Process Entry')
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
    data['form']['company_id'] = user.company_id.id
    return data['form']

def _data_save(self, cr, uid, data, context):

    if not data['form']['sure']:
        raise wizard.except_wizard('UserError', 'Process canceled, please check that you have a data backup and tick the confirmation box !')
    
    pool = pooler.get_pool(cr.dbname)
    self.pool = pool
    mode = 'done'
    company= data['form']['company_id']
    net_account = data['form']['net_income_acct_id']
    if net_account !='':
        for period in data['form']['periods'][0][2]:
            created_move = False
            # skip period if already closed
            jp_ids = self.pool.get('account.journal.period').search(cr, uid, [('period_id', '=', period)]) 
            if jp_ids:
                # get state for first journal period record for this period (all journal period records should be same)
                journal_period_state = self.pool.get('account.journal.period').read(cr, uid, jp_ids, ['state'])[0]['state']
                p_ids = self.pool.get('account.period').search(cr, uid, [('id', '=', period)])
                # get the state for the first account period record for this period (all account period records should be same)
                period_state = self.pool.get('account.period').read(cr, uid, p_ids, ['state'])[0]['state']
                if journal_period_state == 'done' and period_state == 'done':
                    continue
                name = data['form']['report_name']+' ('+self.pool.get('account.period').read(cr, uid, p_ids, ['name'])[0]['name']+')'
                
                for accttype in ['income', 'expenses']:
                    query = 'SELECT id FROM "res_report_attribute" WHERE type=%s and code = %s and company_id=%s'
		    cr.execute(query, ('level1',accttype, company,))
		    accttype_id = cr.fetchall()
		    if not accttype_id:
	                raise osv.except_osv(_('Error !'), _('Closing process is based on the level 1 attribute set for account_account_type (either "income" or "expenses"). Those attributes are missing in table "res_report_attribute" ("account report attributes" Form).'))
                    #We get first the related account_type ids corresponding with the income/expenses classification
                    sub_query = 'select id from "account_account_type" where level1 = %s and company_id = %s order by code' 
                    query = 'select id from "account_account" where user_type in ('+sub_query+') and active order by code' 
                    cr.execute(query, (accttype_id[0], company,))
                    ids = map(lambda x: x[0], cr.fetchall())
                    
                    if not ids:
                        #no account_ids found for the period, we exit the for loop 
                        continue
                    for account in pool.get('account.account').browse(cr, uid, ids):
                        if account.type == 'view':
                            continue
                        # BY BALANCE THAT IS ATTRIBUTABLE TO PERIOD TRANSACTIONS AND NOT BY TOTAL ACCOUNT BALANCE
                        credit_period_balance = _get_account_period_total(self, cr, uid, data, context={'fieldname':'credit', 'account_id':account.id, 'period_id':period})
                        debit_period_balance = _get_account_period_total(self, cr, uid, data, context={'fieldname':'debit', 'account_id':account.id, 'period_id':period})
                        account_period_balance = credit_period_balance - debit_period_balance
                        ## continue  #testing
                        if abs(account_period_balance) < 0.0001:
                            continue
                            #balance to zero so we get out of the loop
                        # create move header
                        if not(created_move):
                            move_id = pool.get('account.move').create(cr, uid, {
                            	'name': name,
                            	'journal_id': data['form']['report_journal'],
                            	'state': 'draft',
                            	'period_id': period,
                            	'ref': '',
                            	'company_id':company,
                            }, {'journal_id': data['form']['report_journal'], 'period_id':period,'company_id': company})
                            created_move=True
                        
                        # create move_lines
                        # income:  increase (credit) the net income summary account by account balance
                        # expense: decrease (debit)  the net income summary account by account balance
                        # we have to create separate lines: 1 for debit, 1 for credit to avoid check 
                        # constraints in database that says at least debit or credit must be 0.
                        if credit_period_balance > 0.00:
                            pool.get('account.move.line').create(cr, uid, {
                            	'debit':        0.00,
                            	'credit':	credit_period_balance,
                            	'name':		name,
                            	'date':		now().date,
                            	'move_id':	move_id,
                            	'journal_id':	data['form']['report_journal'],
                            	'period_id':	period,
                            	'account_id':	net_account,
                            	'company_id':	company,
                            }, {'journal_id':   data['form']['report_journal'], 'period_id':period,'company_id': company})
                            pool.get('account.move.line').create(cr, uid, {
                                'debit':        credit_period_balance,
                                'credit':       0.00,
                                'name':         name,
                                'date':         now().date,
                                'move_id':      move_id,
                                'journal_id':   data['form']['report_journal'],
                                'period_id':    period,
                                'account_id':   account.id,
                                'company_id':   company,
                            }, {'journal_id':   data['form']['report_journal'], 'period_id':period,'company_id': company})
                        
                        if debit_period_balance > 0.00:
                            pool.get('account.move.line').create(cr, uid, {
                            	'debit':	debit_period_balance,
                            	'credit':	0.00,
                            	'name':		name,
                            	'date':		now().date,
                            	'move_id':	move_id,
                            	'journal_id':	data['form']['report_journal'],
                            	'period_id':	period,
                            	'account_id':	net_account,
                            	'company_id':	company,
                            }, {'journal_id':   data['form']['report_journal'], 'period_id':period,'company_id': company})
                            pool.get('account.move.line').create(cr, uid, {
                                'debit':        0.00,
                                'credit':       debit_period_balance,
                                'name':         name,
                                'date':         now().date,
                                'move_id':      move_id,
                                'journal_id':   data['form']['report_journal'],
                                'period_id':    period,
                                'account_id':   account.id,
                                'company_id':   company,
                            }, {'journal_id':   data['form']['report_journal'], 'period_id':period,'company_id': company})

    # close period (mark it 'done')
    query_periods_list= ')'.join(str('('.join(str(data['form']['periods'][0][2]).split('['))).split(']'))
    cr.execute('UPDATE account_journal_period ' \
            'SET state = %s ' \
            'WHERE period_id IN '+query_periods_list,
            (mode,))
    cr.execute('UPDATE account_period SET state = %s ' \
            'WHERE id IN '+query_periods_list,
            (mode,))
    return {}

class wizard_multi_company_period_close(wizard.interface):
    states = {
    	'init': {
    		'actions': [_data_load],
    		'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('close','Close Periods')]}
    	},
    	'close': {
    		'actions': [_data_save],
    		'result': {'type': 'state', 'state':'end'}
    	}
    }
wizard_multi_company_period_close('elico_multi_company_year_end_process.multi.company.period.close')

