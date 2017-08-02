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

import wizard
import osv
import time
import pooler
from tools.translate import _

_transaction_form = '''<?xml version="1.0"?>
<form string="Multi-Company Opening Period Wizard">
    <separator string="Select Company and Closing Fiscal Year" colspan="4"/>
    <field name="company_id"/>  
    <field name="ofy_id"/>
    
    <separator string="Details for the opening period" colspan="4"/>
    <field name="nfy_id"/>
    <field name="journal_id"/>
    <field name="period_id"/>
    <field name="report_name" colspan="4"/>
    
    <separator string="Write-off Information" colspan="4"/>   
    <field name="writeoff_acc_id" colspan="4"/>
    <field name="writeoff_journal_id"/>
    <field name="writeoff_period_id"/>

    <separator string="Are you sure you want to create entries?" colspan="4"/>
    <field name="sure"/>
</form>'''

_transaction_fields = {
    'company_id': {
        'string':'Company', 
        'type':'many2one', 
        'relation': 'res.company',
#        'domain':"[('company_id','child_of',user.company_id)]",
        'help': 'Company to be opened.', 
        'required':True
    }, 
    'ofy_id': {
        'string':'Previous Fiscal Year', 
        'type':'many2one', 
        'relation': 'account.fiscalyear',
        'domain':"[('state','=','draft'),('company_id','=',company_id)]",
        'help': 'Fiscal Year to end.', 
        'required':True
    },
    'journal_id': {
        'string':'Opening Entries Journal', 
        'type':'many2one', 
        'relation': 'account.journal',
        'domain':"[('company_id','=',company_id)]",
        'help': 'Select a Opening Journal or a Journal to record the opening entries.', 
        'required':True
    },
    'period_id': {
        'string':'Opening Entries Period', 
        'type':'many2one', 
        'relation': 'account.period',
        'required':True, 
        'help': 'Period that will contain all the opening entries (eg: 00/20xx).', 
        'domain':"[('fiscalyear_id','=',nfy_id),('company_id','=',company_id)]"
    },
    'nfy_id': {
        'string':'New Fiscal Year', 
        'type':'many2one', 
        'relation': 'account.fiscalyear', 
        'domain':"[('state','=','draft'),('company_id','=',company_id)]",
        'help': 'New fiscal Year to start.', 
        'required':True
    },
    'report_name': {
        'string':'Opening Period Process Entry', 
        'type':'char', 
        'help': 'Default description of the accounting entries.', 
        'size': 64, 
        'required':True
    },
    'writeoff_acc_id': {
        'string': 'Account',
        'type': 'many2one',
        'relation': 'account.account',
        'required': True
    },
    'writeoff_journal_id': {
        'string': 'Journal',
        'type': 'many2one',
        'relation': 'account.journal',
        'domain':"[('company_id','=',company_id)]", 
        'required': True
    },
    'writeoff_period_id': {
        'string': 'Period',
        'type': 'many2one',
        'relation': 'account.period',
        'domain':"[('company_id','=',company_id)]", 
        'required': True
    },
    'sure': {
        'string':'Check this box (Backup recommended)', 
        'type':'boolean'
    },
}

def _data_load(self, cr, uid, data, context):
    data['form']['report_name'] = _('Opening Period Process Entry')
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
    data['form']['company_id'] = user.company_id.id
    return data['form']

def _test_input(cr, uid, data, pool, context):
    """Check if the fiscal year and the account and the wizard form inputs are valids"""
    ##validate the fy
    fy = pool.get('account.fiscalyear').browse(cr, uid, data['form']['ofy_id'])
    fy2 = pool.get('account.fiscalyear').browse(cr, uid, data['form']['nfy_id'])
    ## date of cloture
    date_stopfy = time.strptime(fy.date_stop, '%Y-%m-%d')
    ## date op openning
    date_startfy2 = time.strptime(fy2.date_start, '%Y-%m-%d')
    
    if (fy.state == 'done') or (fy2.state == 'done') :
        raise wizard.except_wizard('UserError',
                'One of the selected fiscal year is aleready closed') 
                
    if date_stopfy > date_startfy2 :
        raise wizard.except_wizard('UserError',
                'The Fiscal Year must be successive') 
    ## we get all the fiscal year start date that are not in the selecte one
    cr.execute('select name, date_start, state from account_fiscalyear where \
    id not in(%d,%d) \
    and company_id =%d',
    (fy.id, fy2.id, data['form']['company_id']))
    res = cr.dictfetchall()
    if res :
    ## we test if there is a fiscal year open between 
        for fy_to_test in res :
            date_to_test = time.strptime(fy_to_test['date_start'], '%Y-%m-%d')
            if date_to_test > date_stopfy \
            and date_to_test < date_startfy2 :
                raise wizard.except_wizard('UserError',
                'there is a fiscal year between the one you want to close : '\
                +fy_to_test['name']) 
    ## we test if all the previous fiscal year are closed
        for fy_to_test in res :
            date_to_test = time.strptime(fy_to_test['date_start'], '%Y-%m-%d')
            if date_to_test < date_stopfy \
            and fy_to_test['state'] != 'done' :
                raise wizard.except_wizard('UserError',
                'there can not be an unclose fiscal year before the one you want to close : '\
                +fy_to_test['name']) 
    return True  

def _data_save(self, cr, uid, data, context):

    if not data['form']['sure']:
        raise wizard.except_wizard(_('UserError'), _('Process canceled, please check that you have a data backup and tick the confirmation box !'))
    pool = pooler.get_pool(cr.dbname)
    _test_input(cr, uid, data, pool, context)

    company = data['form']['company_id']
    nfy_id = data['form']['nfy_id']
    ofy_id = data['form']['ofy_id']
    period = pool.get('account.period').browse(cr, uid, data['form']['period_id'], context=context)
    new_journal = pool.get('account.journal').browse(cr, uid, data['form']['journal_id'], context=context)

    old_fyear = pool.get('account.fiscalyear').browse(cr, uid, ofy_id, context=context)
    ofy_period_ids = pool.get('account.period').search(cr, uid, [('fiscalyear_id', '=', ofy_id)])
    ofy_period_set = ','.join(map(str, ofy_period_ids))

    new_fyear = pool.get('account.fiscalyear').browse(cr, uid, nfy_id, context=context)
    nfy_periods_ids = pool.get('account.period').search(cr, uid, [('fiscalyear_id', '=', nfy_id)])
    nfy_period_set = ','.join(map(str, nfy_periods_ids))


    if not new_journal.default_credit_account_id or not new_journal.default_debit_account_id:
        raise wizard.except_wizard(_('UserError'),
                _('The journal must have default credit and debit account'))
    if not new_journal.centralisation:
        raise wizard.except_wizard(_('UserError'),
                _('The journal must have centralised counterpart'))

    move_ids = pool.get('account.move.line').search(cr, uid, [
        ('journal_id','=',new_journal.id),('period_id.fiscalyear_id','=',new_fyear.id)])
    if move_ids:
        raise wizard.except_wizard(_('UserError'),
                _('The opening journal must not have any entry in the new fiscal year !'))

    query_line = pool.get('account.move.line')._query_get(cr, uid,
            obj='account_move_line', context={'fiscalyear': ofy_id})
    cr.execute('select id from account_account WHERE active and company_id=%s',
		(company,)) 

    ids = map(lambda x: x[0], cr.fetchall())
#    print 'ids'+str(ids)
    for account in pool.get('account.account').browse(cr, uid, ids,
        context={'fiscalyear': ofy_id}):

        accnt_type_data = account.user_type
        print 'account/account_type/balance/closing'+str(account) + str(accnt_type_data)+str(account.balance)+str(accnt_type_data.close_method)
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
                print "result"+str(result)
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
                    print 'move après='+str(move)
                    print" "
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
    ids = pool.get('account.move.line').search(cr, uid, [('journal_id','=',new_journal.id),
        ('period_id.fiscalyear_id','=',new_fyear.id)]) 
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
                'WHERE id = %s', (ids[0], old_fyear.id))

    return {}

class wizard_multi_company_period_open(wizard.interface):
    states = {
        'init': {
            'actions': [_data_load],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('close','Create entries')]}
        },
        'close': {
            'actions': [_data_save],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wizard_multi_company_period_open('elico_multi_company_year_end_process.multi.company.period.open')

