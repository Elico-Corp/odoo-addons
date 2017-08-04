# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

import time
from openerp.report import report_sxw
from common_report_header import common_report_header
from openerp.tools.translate import _

class report_account_common(report_sxw.rml_parse, common_report_header):
    _inherit = 'account.report_account_common'
    def __init__(self, cr, uid, name, context=None):
        super(report_account_common, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'get_lines': self.get_lines,
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_lines_1' : self.get_lines_1,
        })
        self.context = context
    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=data['form']['used_context'])
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
                'report_type' : (report.name == 'Assets' and 'A') or 'L'
            }
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=data['form']['comparison_context']).balance * report.sign or 0.0
            lines.append(vals)
            account_ids = []
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            if account_ids:
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=data['form']['used_context']):
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    flag = False
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance':  account.balance != 0 and account.balance * report.sign or account.balance,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and min(account.level + 1,6) or 6, #account.level + 1
                        'account_type': account.type,
                        'report_type' : (report.name == 'Assets' and 'A') or 'L'
                    }

                    if data['form']['debit_credit']:
                        vals['debit'] = account.debit
                        vals['credit'] = account.credit
                    if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance']):
                        flag = True
                    if data['form']['enable_filter']:
                        vals['balance_cmp'] = account_obj.browse(self.cr, self.uid, account.id, context=data['form']['comparison_context']).balance * report.sign or 0.0
                        if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines
    def get_lines_1(self, data):
        lines = self.get_lines(data)
        l_line = []
        a_line = []
        res = []
        for l in lines:
            if l['report_type'] == 'L':
                l_line.append(l)
            else:
                a_line.append(l)
        if len(l_line) == len(a_line):
            res.append([{'L':l_line[0]},{'A':l_line[0]}])
            for n in range(1,len(l_line)):
                res.append([{'L':l_line[n]},{'A':a_line[n-1]}])
            res.append([{'L':{'level':3,'account_type': 'n'}},{'A':a_line[-1]}])
            return res
        elif len(l_line) > len(a_line):
            res.append([{'L':l_line[0]},{'A':l_line[0]}])
            for n in range(1,len(a_line)):
                res.append([{'L':l_line[n]},{'A':a_line[n-1]}])
            if len(l_line) == len(a_line) + 1:
                res.append({[{'L':l_line[-1]},{'A':a_line[-1]}]})
                return res
            
            if a_line: #LY
                try:
                    res.append({[{'L':l_line[len(a_line)]},{'A':a_line[-1]}]})
                except:
                    import pdb; pdb.set_trace()
                    #LY150402.
            for n in range(len(a_line)+1,len(l_line)):
                res.append([{'L':l_line[n]},{'A':{'level':3,'account_type': 'n'}}])
            return res
        elif len(a_line) > len(l_line):
            res.append([{'L':l_line[0]},{'L':l_line[0]}])
            for n in range(1,len(l_line)):
                res.append([{'L':l_line[n]},{'A':a_line[n-1]}])
            for n in range(len(l_line)-1,len(a_line)):
                res.append([{'L':{'level':3,'account_type': 'n'}},{'A':a_line[n]}])
            return res


report_sxw.report_sxw(
    'report.account.financial.report.extended',
    'account.financial.report',
    'addons/balance_sheet_extended/report/account_financial_report.rml',
    parser=report_account_common, header='internal')