# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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

import time
import datetime
from report import report_sxw
from report.report_sxw import rml_parse
import netsvc
from osv import osv
from tools import ustr
import pooler

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        datenow = datetime.datetime.now()
        self.localcontext.update({
            'time':      datenow.strftime("%Y-%m-%d %H:%M:%S"),
            'myheaders': self.get_cols(context=context),
            'mylines':   self.get_lines(context=context),
        })
    
    
    def get_cols(self, context=None):
        if not context:
            context = {}
        
        res          = {}
        result       = []
        ranges_list  = []
        active_ids   = context.get('active_ids', [])
        
        # Report Currency
        res['currency'] = "USD"
        company_pool = self.pool.get('res.company')
        company_id   = company_pool._company_default_get(self.cr, self.uid, 'gap_analysis', context=context)
        if company_id:
            company  = company_pool.browse(self.cr, self.uid, company_id)
            res['currency'] = company.currency_id.name
            context.update({'currency_symbol':company.currency_id.symbol})
        
        # List of Columns
        for cpt in range(1, 18):# Set default value
            range_name = "range" + str(cpt)
            res[range_name] = ""
        
        cpt = 1
        self.cr.execute("SELECT id, name FROM gap_analysis_workload_type ORDER BY sequence ASC")
        ranges = self.cr.fetchall()
        for idx, one_range in enumerate(ranges):
            range_name = "range" + str(cpt)
            ranges_list.append(one_range[0])
            res[range_name] = str(one_range[1])
            cpt += 1
        
        result.append(res)
        context.update({'workload_type_list':ranges_list})
        return result            
    
    
    def get_lines(self, context=None):
        if not context:
            context = {}
        
        result         = []
        all_categ_ids  = []
        gap_categ_ids  = []
        cpt            = {}
        active_id      = context.get('active_id', False)
        currency       = context.get('currency_symbol', '$')
        gap_pool       = self.pool.get('gap_analysis')
        
        total_cost          = 0
        total_analysis      = 0
        total_dev           = 0
        total_cost_keep     = 0
        total_analysis_keep = 0
        total_dev_keep      = 0
        
        if active_id:
            # First we get all the used category for this Gap Analysis
            active_gap = gap_pool.browse(self.cr, self.uid, active_id)
            for one_line in active_gap.gap_lines:
                res = {}
                
                res['functionality'] = one_line.functionality.name
                res['description']   = one_line.functionality.description or one_line.functionality.name
                res['fct_category']  = one_line.category.full_path or one_line.category.name
                res['phase']         = one_line.phase
                res['critical']      = one_line.critical
                res['keep']          = "Keep"
                res['openerp_fct']   = one_line.openerp_fct and one_line.openerp_fct.name or ''
                res['contributor']   = one_line.contributors or ''
                res['effort']        = one_line.effort and one_line.effort.name or ''
                res['effort2day']    = ''
                res['cpt']           = one_line.code
                res['testing']       = one_line.testing
                
                res['total_cost']    = one_line.total_cost or 0
                
                if one_line.effort and one_line.effort.unknown:
                    res['effort2day'] = one_line.duration_wk
                
                if one_line.effort:
                    if one_line.effort.unknown:
                        res['total_dev'] = one_line.duration_wk
                    else:
                        res['total_dev'] = one_line.effort.duration
                    res['total_analysis'] = one_line.total_time - res['total_dev']
                else:
                    res['total_dev'] = 0
                    res['total_analysis'] = one_line.total_time
                
                if res['total_analysis'] <= 0:
                    res['total_analysis'] = 0
                
                
                if res['total_cost'] == '':
                    tmp_cost = 0
                else:
                    tmp_cost = res['total_cost']
                if res['total_analysis'] == '':
                    tmp_analysis = 0
                else:
                    tmp_analysis = res['total_analysis']
                if res['total_dev'] == '':
                    tmp_dev = 0
                else:
                    tmp_dev = res['total_dev']
                
                
                if not one_line.keep:
                    res['keep'] = "DROP"
                    total_cost          += tmp_cost
                    total_analysis      += tmp_analysis
                    total_dev           += tmp_dev
                else:
                    total_cost          += tmp_cost
                    total_analysis      += tmp_analysis
                    total_dev           += tmp_dev
                    total_cost_keep     += tmp_cost
                    total_analysis_keep += tmp_analysis
                    total_dev_keep      += tmp_dev
                
                
                for ii in range(1, 18):# Set default value
                    cost_name = "cost" + str(ii)
                    res[cost_name] = ''
                
                ii = 1
                for one_type in context['workload_type_list']:
                    for one_workload in one_line.workloads:#for each possible Workload Type                            
                        if one_workload.type.id == one_type:
                            cost_name = "cost" + str(ii)
                            res[cost_name] = str(one_workload.duration)
                    ii += 1
                result.append(res)
        
        return result
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
