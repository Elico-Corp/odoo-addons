# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from tools.translate import _

class gap_analysis_wizard(osv.TransientModel):
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


class gap_analysis_tasks_list(osv.TransientModel):
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

