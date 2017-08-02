# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import pooler

class financial_statements_report(osv.osv_memory):
    """
    For Multi-company reports
    """
    _inherit = "account.common.account.report"
    _name = "multicompany.report"
    _description = "Multi-company Report"
    _columns = {
    'company_id': fields.many2one(
        'res.company',
        'Company', 
        help='Company for which we want the report.',
        required=True
        ), 
    'fiscalyear1': fields.many2one(
        'account.fiscalyear', 
        'Main Fiscal Year',
        help='Main Fiscal Year for which we want the report.',
        required=True
        ),
    'periods1': fields.many2many(
        'account.period',
 	'account_period_rel',
	'period_id',
	'periods1',
        'Main Periods', 
        help='Main periods for Report.',
        required=True
        ),
    'compared': fields.boolean(
        'Compare 2 range of periods', 
        help='Check this box if you want to compare 2 periods at the same time.', 
        ),

    'fiscalyear2': fields.many2one(
        'account.fiscalyear', 
        'Compared Fiscal Year', 
        help='Comparative Fiscal Year for which we want the report.'
        ),

    'periods2': fields.many2many(
        'account.period', 
 	'account_period_rel',
	'period_id',
	'periods2',
        'Compared Periods', 
        help='Comparative periods for Report.'
        ),
    'report_type': fields.selection(
        [('ISRep','Income Statement'),
         ('BSRep','Statement of Financial Position')],
        'Choose the Report Type', 
        help='Choose the kind of report you want to see.', 
        required=True
        ),
     'report_details': fields.selection(
        [('RepSum','Summary'),
         ('RepSim','Simple'),
         ('RepDet','Detailed'),
         ('RepCus','Customized')],
        'Choose the Report details', 
        help='Choose the report details you want to see.', 
        required=True
        ),
    'skip_accts_no_activity': fields.boolean(
        'Skip Accounts with no Activity', 
        help='Check this box to skip accounts with no activity (debit = 0 and credit = 0)', 
        ),
    'hide_accounts': fields.boolean(
        'Hide Account Details', 
        help='Check this box to hide the listing of accounts; will only display summaries.', 
        ),
    'hide_view_accounts': fields.boolean(
        'Hide "view" Type Account', 
        help='Check this box to hide the accounts with specific "view" type.', 
        ),
    'field_1': fields.selection(
        [('level1','Level 1 Attribute'),
         ('level2','Level 2 Attribute'),
         ('user_type','User-Type Attribute'),
         ('current','Current Flag Attribute'),
         ('operating','Operating Flag Attribute')],
        '1st Field Information', 
        required=True,
        help='Select the attribute details you want to show for this level.'
        ),
    'field_2': fields.selection(
        [('level1','Level 1 Attribute'),
         ('level2','Level 2 Attribute'),
         ('user_type','User-Type Attribute'),
         ('current','Current Flag Attribute'),
         ('operating','Operating Flag Attribute')],
        '2nd Field Information', 
        help='Select the attribute details you want to show for this level.'
        ),
    'field_3': fields.selection(
        [('level1','Level 1 Attribute'),
         ('level2','Level 2 Attribute'),
         ('user_type','User-Type Attribute'),
         ('current','Current Flag Attribute'),
         ('operating','Operating Flag Attribute')],
        '3rd Field Information', 
        help='Select the attribute details you want to show for this level.'
        ),
    'field_4': fields.selection(
        [('level1','Level 1 Attribute'),
         ('level2','Level 2 Attribute'),
         ('user_type','User-Type Attribute'),
         ('current','Current Flag Attribute'),
         ('operating','Operating Flag Attribute')],
        '4th Field Information', 
        help='Select the attribute details you want to show for this level.'
        ),
    'field_5': fields.selection(
        [('level1','Level 1 Attribute'),
         ('level2','Level 2 Attribute'),
         ('user_type','User-Type Attribute'),
         ('current','Current Flag Attribute'),
         ('operating','Operating Flag Attribute')],
        '5th Field Information', 
        help='Select the attribute details you want to show for this level.'
        ),
    'c_field_1': fields.boolean(
        'Cumulative Totals', 
        help='Check box to create cumulative totals for the attribute.', 
        ),
    'c_field_2': fields.boolean(
        'Cumulative Totals', 
        help='Check box to create cumulative totals for the attribute.', 
        ),
    'c_field_3': fields.boolean(
        'Cumulative Totals', 
        help='Check box to create cumulative totals for the attribute.', 
        ),
    'c_field_4': fields.boolean(
        'Cumulative Totals', 
        help='Check box to create cumulative totals for the attribute.', 
        ),
    'c_field_5': fields.boolean(
        'Cumulative Totals', 
        help='Check box to create cumulative totals for the attribute.', 
        ),
}

    def _get_default_fiscalyear(self, cr, uid, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        return fiscalyear_obj.find(cr, uid)

    def _get_default_company_id(self, cr, uid, context):
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id


    _defaults={
        'compared':False,
	'fiscalyear1':_get_default_fiscalyear,
	'company_id':_get_default_company_id,
        'report_type':'ISRep',
        'report_details':'RepDet',
        'skip_accts_no_activity':True,
        'hide_accounts':False,
        'hide_view_accounts':True,
        'field_1':'level1',
        'c_field_1':False,
        'c_field_2':False,
        'c_field_3':False,
        'c_field_4':False,
        'c_field_5':False,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids, ['company_id',  'compared', 'fiscalyear1', 'periods1', 'fiscalyear2',
			 'periods2','report_type','report_details','skip_accts_no_activity','hide_accounts','hide_view_accounts',
			'field_1', 'c_field_1','field_2', 'c_field_2','field_3', 'c_field_3','field_4', 'c_field_4','field_5', 'c_field_5' ])[0])
	if data['form']['compared']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account_financial_statements.financial.statements.compared.report',
                'datas': data,
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account_financial_statements.financial.statements.report',
                'datas': data,
            }

financial_statements_report()
