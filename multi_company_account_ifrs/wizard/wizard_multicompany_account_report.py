##############################################################################
#
# Copyright 2010 Eric Caudal,   All Rights Reserved.
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

dates_form = '''<?xml version="1.0"?>
<form string="Multi-Company Compared Reports">
 
    <separator string="Report's Company and Fiscal Year" colspan="4"/>
       <field name="company_id"/>  
 
    <separator string="Report's Accounting periods" colspan="4"/>
        <field name="fiscalyear1"/>
        <field name="periods1" colspan="4"/>
        <field name="fiscalyear2"/>
        <field name="periods2" colspan="4"/>
 
    <separator string="Report's Options" colspan="4"/>
    <field name="report_type"/>
    <group attrs="{'invisible':[('report_type','=','OTRep')]}">
        <field name="report_details"/>
    </group>
    
    <field name="skip_accts_no_activity"  colspan="4"/>
    <field name="hide_accounts"  colspan="4"/>
    <field name="hide_view_accounts"  colspan="4"/>

    <group attrs="{'invisible':[('report_details','!=','RepCus')]}" colspan="4">
        <separator string="Customized Report's options" colspan="4"/>
        <field name="field_1" />
        <field name="c_field_1" />
        <field name="field_2" />
        <field name="c_field_2"/>
        <field name="field_3"/>
        <field name="c_field_3"/>
        <field name="field_4"/>
        <field name="c_field_4"/>
        <field name="field_5"/>
        <field name="c_field_5"/>
    </group>
</form>'''

dates_fields = {
    'company_id': {
        'string':       'Company', 
        'type':         'many2one', 
        'relation':     'res.company',
        'help':         'Company for which we want the report.',
        'required':     True
    }, 
    'fiscalyear1': {
        'string':       'Main Fiscal Year', 
        'type':         'many2one', 
        'relation':     'account.fiscalyear', 
        'domain':       "[('company_id','=',company_id)]",
        'help':         'Main Fiscal Year for which we want the report.',
        'required':     True
    },
    'fiscalyear2': {
        'string':       'Compared Fiscal Year', 
        'type':         'many2one', 
        'relation':     'account.fiscalyear', 
        'domain':       "[('company_id','=',company_id)]",
        'help':         'Comparative Fiscal Year for which we want the report.'
    },
    'periods1': {
        'string':       'Main Periods', 
        'type':         'many2many', 
        'relation':     'account.period', 
        'domain':       "[('fiscalyear_id','=',fiscalyear1),('company_id','=',company_id)]",
        'help':         'Main periods for Report.',
        'required':     True
    },
    'periods2': {
        'string':       'Compared Periods', 
        'type':         'many2many', 
        'relation':     'account.period', 
        'domain':       "[('fiscalyear_id','=',fiscalyear2),('company_id','=',company_id)]",
        'help':         'Comparative periods for Report.'
    },
    'report_type': {
        'string':       'Choose the Report Type', 
        'type':         'selection', 
        'selection':    [('ISRep','Income Statement'),
                         ('BSRep','Statement of Financial Position')],
        'help':         'Choose the kind of report you want to see.', 
        'default':      'ISRep',
        'required':     True
        },
     'report_details': {
        'string':       'Choose the Report details', 
        'type':         'selection', 
        'selection':    [('RepSum','Summary'),
                         ('RepSim','Simple'),
                         ('RepDet','Detailed'),
                         ('RepCus','Customized')],
        'help':         'Choose the report details you want to see.', 
        'default':      'RepSum',
        'required':     True
        },
    'skip_accts_no_activity': {
        'string':       'Skip Accounts with no Activity', 
        'type':         'boolean', 
        'help':         'Check this box to skip accounts with no activity (debit = 0 and credit = 0)', 
        'default':      lambda *a: True
        },
    'hide_accounts': {
        'string':       'Hide Account Details', 
        'type':         'boolean', 
        'help':         'Check this box to hide the listing of accounts; will only display summaries.', 
        'default':      lambda *a: True
        },
    'hide_view_accounts': {
        'string':       'Hide "view" Type Account', 
        'type':         'boolean', 
        'help':         'Check this box to hide the accounts with specific "view" type.', 
        'default':      lambda *a: True
        },
    'field_1': {
        'string':       '1st Field Information', 
        'type':         'selection', 
        'selection':    [('level1','Level 1 Attribute'),
                         ('level2','Level 2 Attribute'),
                         ('user_type','User-Type Attribute'),
                         ('current','Current Flag Attribute'),
                         ('operating','Operating Flag Attribute')],
        'required':     True,
        'default':      'level1',
        'help':         'Select the attribute details you want to show for this level.'
        },
    'field_2': {
        'string':       '2nd Field Information', 
        'type':         'selection', 
        'selection':    [('level1','Level 1 Attribute'),
                         ('level2','Level 2 Attribute'),
                         ('user_type','User-Type Attribute'),
                         ('current','Current Flag Attribute'),
                         ('operating','Operating Flag Attribute')],
        'help':         'Select the Attribute details you want to show for this level.' 
        },
    'field_3': {
        'string':       '3rd Field Information', 
        'type':         'selection', 
        'selection':    [('level1','Level 1 Attribute'),
                         ('level2','Level 2 Attribute'),
                         ('user_type','User-Type Attribute'),
                         ('current','Current Flag Attribute'),
                         ('operating','Operating Flag Attribute')],
        'help':         'Select the attribute details you want to show for this level.' 
        },
    'field_4': {
        'string':       '4th Field Information', 
        'type':         'selection', 
        'selection':    [('level1','Level 1 Attribute'),
                         ('level2','Level 2 Attribute'),
                         ('user_type','User-Type Attribute'),
                         ('current','Current Flag Attribute'),
                         ('operating','Operating Flag Attribute')],
        'help':         'Select the attribute details you want to show for this level.' 
        },
    'field_5': {
        'string':       '5th Field Information', 
        'type':         'selection', 
        'selection':    [('level1','Level 1 Attribute'),
                         ('level2','Level 2 Attribute'),
                         ('user_type','User-Type Attribute'),
                         ('current','Current Flag Attribute'),
                         ('operating','Operating Flag Attribute')],
        'help':         'Select the attribute details you want to show for this level.' 
        },
    'c_field_1': {
        'string':       'Cumulative Totals', 
        'type':         'boolean', 
        'help':         'Check box to create cumulative totals for the attribute.', 
        'default':      lambda *a: False
        },
    'c_field_2': {
        'string':       'Cumulative Totals', 
        'type':         'boolean', 
        'help':         'Check box to create cumulative totals for the attribute.', 
        'default':      lambda *a: False
        },
    'c_field_3': {
        'string':       'Cumulative Totals', 
        'type':         'boolean', 
        'help':         'Check box to create cumulative totals for the attribute.', 
        'default':      lambda *a: False
        },
    'c_field_4': {
        'string':       'Cumulative Totals', 
        'type':         'boolean', 
        'help':         'Check box to create cumulative totals for the attribute.', 
        'default':      lambda *a: False
        },
    'c_field_5': {
        'string':       'Cumulative Totals', 
        'type':         'boolean', 
        'help':         'Check box to create cumulative totals for the attribute.', 
        'default':      lambda *a: False
        },
}

class wizard_report(wizard.interface):
    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear1'] = fiscalyear_obj.find(cr, uid)
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        data['form']['company_id'] = user.company_id.id
        return data['form']
    
    states ={
        'init': 
            {
            'actions': [_get_defaults],
            'result': 
                {
                'type':'form', 
                'arch':dates_form, 
                'fields':dates_fields, 
                'state':[
                         ('end','Cancel'),
                         ('Print','Print Report'),
                         ('PrintComp','Print Compared Report')]
                },
            },
        'Print': 
            {
            'actions': [],
            'result':
                {
                'type':'print', 
                'report':'multi_company_account_ifrs.multicompany.account.report', 
                'state':'end'
                },
            },
        'PrintComp': 
            {
            'actions': [],
            
            'result':
                {
                'type':'print', 
                'report':'multi_company_account_ifrs.multicompany.account.compared.report', 
                'state':'end'
                },
            },
    }
wizard_report('multi_company_account_ifrs.multicompany.account.report')

