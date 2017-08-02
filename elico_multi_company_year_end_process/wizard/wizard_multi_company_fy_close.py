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
import pooler
from tools.translate import _

_transaction_form = '''<?xml version="1.0"?>
<form string=" Close Fiscal year, periods and Journal for a given fiscal year.">
    <separator string="Select Company and Fiscal Year to be closed" colspan="4"/>
    <field name="company_id"/>  
    <field name="fy_id"/>
    <separator string="Are you sure you want to close the fiscal year ?" colspan="4"/>
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
    'fy_id':
        {
        'string':'Fiscal Year to be closed',
        'type':'many2one', 
        'relation': 'account.fiscalyear',
        'required':True, 
        'domain':"[('state','=','draft'),('company_id','=',company_id)]",
        'help': 'Fiscal Year to be closed.', 
        },
    'sure': 
        {
        'string':'Check this box (Backup recommended)', 
        'type':'boolean'
        },
}
def _data_load(self, cr, uid, data, context):
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
    data['form']['company_id'] = user.company_id.id
    return data['form']

def _data_save(self, cr, uid, data, context):
    if not data['form']['sure']:
        raise wizard.except_wizard(_('UserError'), _('Process canceled, please check that you have a data backup and tick the confirmation box !'))

    fy_id = data['form']['fy_id']
    company = data['form']['company_id']
    
    cr.execute('UPDATE account_journal_period ' \
            'SET state = %s ' \
            'WHERE period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = %s and company_id = %s)',
            ('done', fy_id, company))
    cr.execute('UPDATE account_period SET state = %s ' \
            'WHERE fiscalyear_id = %s  and company_id= %s', ('done', fy_id, company))
    cr.execute('UPDATE account_fiscalyear ' \
            'SET state = %s WHERE id = %s and company_id= %s', ('done', fy_id, company))
    return {}

class wizard_multi_company_fy_close(wizard.interface):
    states = {
        'init': {
            'actions': [_data_load],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('close','Close states')]}
        },
        'close': {
            'actions': [_data_save],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wizard_multi_company_fy_close('elico_multi_company_year_end_process.multi.company.fy.close')
