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

from datetime import datetime
import time
from osv import fields, osv
from tools.translate import _
from tools import ustr
#import tools


class gap_analysis(osv.osv):
    _inherit = "gap_analysis"
    _name = "gap_analysis"
    
    def generate_project(self, cr, uid, ids, context=None):
        project_pool = self.pool.get('project.project')
        phase_pool   = self.pool.get('project.phase')
        gapline_pool = self.pool.get('gap_analysis.line')
        task_pool    = self.pool.get('project.task')
        uom_hour     = self.pool.get('product.uom').search(cr, uid, [('name', '=', _('Hour'))], context=context)[0]
        
        for gap in self.browse(cr, uid, ids, context=context):
            partner_id = gap.partner_id and gap.partner_id.id or False
            notes      = gap.note or ''
            
            notes = gap.note or ''
            
            project_vals = {
                'name':        gap.name,
                'description': notes,
                'user_id':     gap.user_id.id,
                'partner_id':  partner_id,
                'gap_analysis_id': gap.id,
            }
            project_id = project_pool.create(cr, uid, project_vals, context=context)
            
            phases = {}
            for gap_line in gap.gap_lines:
                if gap_line.to_project and gap_line.keep:
                    time4dev  = 0
                    time4tech = 0
                    time4fct  = 0
                    time4test = gap_line.testing or 0
                    
                    if gap_line.effort:
                        if gap_line.effort.unknown:
                            time4dev = gap_line.duration_wk
                        else:
                            time4dev = gap_line.effort.duration
                        
                    for workload in gap_line.workloads:
                        if workload.type.category == "Technical Analysis":
                            time4tech += workload.duration
                        else:
                            time4fct  += workload.duration
                        
                    #CREATE PROJECT PHASES
                    phase = gap_line.phase or '0'
                    phase = phase.upper()
                    
                    if phase not in phases:
                        gapline_ids = gapline_pool.search(cr, uid, [('gap_id', '=', gap.id),('phase', 'ilike', phase),('keep', '=', True),('to_project', '=', True)])
                        duration_hour = 0
                        if gapline_ids:
                            for l in gapline_pool.browse(cr, uid, gapline_ids):
                                duration_hour += l.total_time
                        
                        phase_vals = {
                            'name':        gap.name + " - " + phase,
                            'project_id':  project_id,
                            'duration':    duration_hour,
                            'product_uom': uom_hour,
                            'previous_phase_ids': [],#TODO
                            'next_phase_ids': [],#TODO
                        }
                        phases[phase] = phase_pool.create(cr, uid, phase_vals, context=context)
                    
                    # Create Tasks
                    if time4dev > 0 or time4tech > 0 or time4fct > 0 or time4test > 0:
                        maintask_vals = {
                            'name': gap_line.functionality.name[0:100],
                            'code_gap': gap_line.code or "",
                            'project_id':    project_id,
                            'notes':         ustr(gap_line.functionality.description or gap_line.functionality.name),
                            'partner_id':    partner_id,
                            'phase_id':      phases[phase],
                            'gap_category_id': gap_line.category and gap_line.category.id or False,
                            'user_id': gap.user_functional and gap.user_functional.id or False,
                            'gap_line_id': gap_line.id,
                            'to_report': True,
                            'org_planned_hours': 0,
                            'planned_hours': 0,
                            'remaining_hours': 0,
                        }
                        maintask_id = task_pool.create(cr, uid, maintask_vals, context=context)
                        maintask_id = [int(maintask_id)]
                        
                    if time4test > 0:
                        task_vals4test = {
                            'name': gap_line.functionality.name[0:100] + " [TEST]",
                            'code_gap': gap_line.code or "",
                            'project_id':    project_id,
                            'notes':         ustr(gap_line.functionality.description or gap_line.functionality.name),
                            'partner_id':    partner_id,
                            'org_planned_hours': time4test,
                            'planned_hours': time4test,
                            'remaining_hours': time4test,
                            'phase_id':      phases[phase],
                            'parent_ids':    [(6,0,maintask_id)],
                            'gap_category_id': gap_line.category and gap_line.category.id or False,
                            'user_id': gap.user_test and gap.user_test.id or False,
                            'gap_line_id': gap_line.id,
                        }
                        task_pool.create(cr, uid, task_vals4test, context=context)
                                            
                    if time4dev > 0:
                        task_vals4dev = {
                            'name': gap_line.functionality.name[0:100] + " [DEV]",
                            'code_gap': gap_line.code or "",
                            'project_id':    project_id,
                            'notes':         ustr(gap_line.functionality.description or gap_line.functionality.name),
                            'partner_id':    partner_id,
                            'org_planned_hours': time4dev,
                            'planned_hours': time4dev,
                            'remaining_hours': time4dev,
                            'phase_id':      phases[phase],
                            'parent_ids':    [(6,0,maintask_id)],
                            'gap_category_id': gap_line.category and gap_line.category.id or False,
                            'user_id': gap.user_dev and gap.user_dev.id or False,
                            'gap_line_id': gap_line.id,
                        }
                        task_pool.create(cr, uid, task_vals4dev, context=context)
                    
                    if time4tech > 0:
                        task_vals4tech = {
                            'name': gap_line.functionality.name[0:100] + " [TECH]",
                            'code_gap': gap_line.code or "",
                            'project_id':    project_id,
                            'notes':         ustr(gap_line.functionality.description or gap_line.functionality.name),
                            'partner_id':    partner_id,
                            'org_planned_hours': time4tech,
                            'planned_hours': time4tech,
                            'remaining_hours': time4tech,
                            'phase_id':      phases[phase],
                            'parent_ids':    [(6,0,maintask_id)],
                            'gap_category_id': gap_line.category and gap_line.category.id or False,
                            'user_id': gap.user_technical and gap.user_technical.id or False,
                            'gap_line_id': gap_line.id,
                        }
                        task_pool.create(cr, uid, task_vals4tech, context=context)
                    
                    if time4fct > 0:
                        task_vals4fct = {
                            'name': gap_line.functionality.name[0:100] + " [FUNC]",
                            'code_gap': gap_line.code or "",
                            'project_id':    project_id,
                            'notes':         ustr(gap_line.functionality.description or gap_line.functionality.name),
                            'partner_id':    partner_id,
                            'org_planned_hours': time4fct,
                            'planned_hours': time4fct,
                            'remaining_hours': time4fct,
                            'phase_id':      phases[phase],
                            'parent_ids':    [(6,0,maintask_id)],
                            'gap_category_id': gap_line.category and gap_line.category.id or False,
                            'user_id': gap.user_functional and gap.user_functional.id or False,
                            'gap_line_id': gap_line.id,
                        }
                        task_pool.create(cr, uid, task_vals4fct, context=context)
        
        if project_id:
            return {
            'type': 'ir.actions.act_window',
            'name':"Generated Project",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'project.project',
            'res_id': project_id,
            'context': context
        }
        return True
    
gap_analysis()


class gap_analysis_line(osv.osv):
    _inherit = "gap_analysis.line"
    _name = "gap_analysis.line"
    
    _columns = {
        'phase': fields.char('Phase', size=4, help='Specify the Phase where the functionality will be done.', required=True),
    }
    _defaults = {
        'phase': lambda *a: 1,
    }
    
    _order = 'phase asc, critical desc, effort asc'
    
gap_analysis_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: