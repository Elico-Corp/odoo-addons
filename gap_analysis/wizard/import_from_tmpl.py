# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from tools.translate import _

class gap_analysis_import_from_tmpl(osv.TransientModel):
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
            #copy gap_line with functionalities and workloads
            for gap_line in this.template.gap_lines:
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
                    'category':      gap_line.category,
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: