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

from osv import osv, fields
from tools.translate import _

class gap_analysis_wizard(osv.osv_memory):
    _name='gap_analysis.gap_analysis_wizard'
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        data = {'model':'gap_analysis', 'ids':context.get('active_ids', []), 'id':ids[0], 'report_type': 'aeroo'}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'gap_analysis',
            'datas': data,
            'context':context
        }
gap_analysis_wizard()


class gap_analysis_tasks_list(osv.osv_memory):
    _name='gap_analysis.tasks_list'
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        data = {'model':'project.task', 'ids':context.get('active_ids', []), 'id': context.get('active_id', ids[0]), 'report_type': 'aeroo'}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tasks_list',
            'datas': data,
            'context':context
        }
gap_analysis_tasks_list()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: