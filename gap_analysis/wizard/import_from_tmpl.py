# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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

from osv import osv, fields
from tools.translate import _

class gap_analysis_import_from_tmpl(osv.osv_memory):
    _name='gap_analysis.import_from_tmpl'
    
    _columns = {
        'template': fields.many2one('gap_analysis', 'Template', required=True, select=True),
    }

    
    def go_import(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        this = self.browse(cr, uid, ids[0], context=context)
        gap_line_pool = self.pool.get('gap_analysis.line')
        workload_pool = self.pool.get('gap_analysis.workload')
               
        for id in context.get('active_ids', []): #for each gap in which we want to import stuff
            current_line_ids = gap_line_pool.search(cr, uid, [('gap_id','=',id)], context=context)
            current_fcts = gap_line_pool.read(cr, uid, current_line_ids, ['functionality'])
            current_fct_ids = [f['functionality'][0] for f in current_fcts]
 
            #copy gap_line with functionalities and workloads
            for gap_line in this.template.gap_lines:

                if gap_line.functionality.id in current_fct_ids:
                    # Functionality already exists in the Gap.
                    continue

                line_vals = {
                    'gap_id':        id,
                    'functionality': gap_line.functionality.id,
                    'workloads':     [],
                    'openerp_fct':   gap_line.openerp_fct and gap_line.openerp_fct.id or False,
                    'contributors':  gap_line.contributors,
                    'keep':          gap_line.keep,
                    'critical':      gap_line.critical,
                    'effort':        gap_line.effort and gap_line.effort.id or False,
                    'duration_wk':   gap_line.duration_wk,
                    'unknown_wk':    gap_line.unknown_wk,
                    'testing':       gap_line.testing,
                    'category':      gap_line.category.id,
                }
                gap_line_id = gap_line_pool.create(cr, uid, line_vals, context=context)
                
                for workload in gap_line.workloads:
                    workload_vals = {
                        'gap_line_id': gap_line_id,        
                        'type':        workload.type.id,
                        'duration':    workload.duration,
                    }
                    workload_id = workload_pool.create(cr, uid, workload_vals, context=context)
        
        return {'type': 'ir.actions.act_window_close'}

gap_analysis_import_from_tmpl()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
