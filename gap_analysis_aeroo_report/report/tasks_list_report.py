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

TASK_PRIORITY = { 
    '4':'Very Low',
    '3':'Low',
    '2':'Medium',
    '1':'Important',
    '0':'Very important',
}

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'myheaders': self.get_cols(context=context),
            'mylines':   self.get_lines(context=context),
        })
    
    
    def get_cols(self, context=None):
        context = context or {}
        res          = {}
        result       = []
        ranges_list  = []
        active_id    = context.get('active_id', False)
        
        if active_id:
            project = self.pool.get('project.project').browse(self.cr, self.uid, active_id)
            res["project"] = 'Project "' + project.name + '"'
            res["customer"] = project.partner_id and project.partner_id.name or 'Customer Undefined'
        else:
            res["project"] = 'Project Undefined'
            res["customer"] = 'Customer Undefined'
        
        res["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        result.append(res)
        return result            
    
    
    def get_lines(self, context=None):
        context = context or {}
        result         = []
        active_id      = context.get('active_id', False)
        task_pool      = self.pool.get('project.task')
        
        if active_id:
            cpt = 0
            task_ids = task_pool.search(self.cr, self.uid, [('project_id','=',active_id),('to_report','=',True)], order='id') or []
            for one_line in task_pool.browse(self.cr, self.uid, task_ids):
                res = {}
                cpt += 1
                duration = one_line.planned_hours or one_line.child_planned_hours or 0
                duration = duration / 8.00#Hours => Days
                
                original_duration = one_line.org_planned_hours or one_line.org_child_planned_hours or 0
                original_duration = original_duration / 8.00#Hours => Days
                
                resolution = 'n/a'
                if one_line.date_start and one_line.date_end:
                    resolution = datetime.datetime.strptime(one_line.date_end, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(one_line.date_start, "%Y-%m-%d %H:%M:%S")
                    resolution = abs(resolution.days)
                
                res['code']          = one_line.gap_line_id and one_line.gap_line_id.code or cpt
                res['category']      = one_line.gap_category_id and one_line.gap_category_id.name or ''
                res['module']        = one_line.module_id and one_line.module_id.name or ''
                res['name']          = one_line.name
                res['assigned']      = one_line.user_id and one_line.user_id.name or ''
                res['start']         = one_line.date_start and one_line.date_start.split()[0] or ''
                res['end']           = one_line.date_end and one_line.date_end.split()[0] or ''
                res['priority']      = one_line.priority in TASK_PRIORITY and TASK_PRIORITY[one_line.priority] or 'n/a'
                res['status']        = one_line.state
                res['org_duration']  = original_duration
                res['duration']      = duration
                res['resolution']    = resolution
                result.append(res)
        
        return result
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: