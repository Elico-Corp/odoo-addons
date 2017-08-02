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
import tools
from tools import ustr


class gap_analysis(osv.osv):
    _inherit = "gap_analysis"
    _name = "gap_analysis"
    
    def generate_project(self, cr, uid, ids, context=None):
        project_pool = self.pool.get('project.project')
        task_pool    = self.pool.get('project.task')
        
        for gap in self.browse(cr, uid, ids, context=context):
            partner_id = gap.partner_id and gap.partner_id.id or False
            notes      = gap.note or ''
            
            project_vals = {
                'name':        gap.name,
                'description': notes,
                'user_id':     gap.user_id.id,
                'partner_id':  partner_id,
                'gap_analysis_id': gap.id,
            }
            project_id = project_pool.create(cr, uid, project_vals, context=context)
            
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
                    
                    # Create Tasks
                    if time4dev > 0 or time4tech > 0 or time4fct > 0 or time4test > 0:
                        maintask_vals = {
                            'name': gap_line.functionality.name[0:100],
                            'code_gap': gap_line.code or "",
                            'project_id':    project_id,
                            'notes':         ustr(gap_line.functionality.description or gap_line.functionality.name),
                            'partner_id':    partner_id,
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
                            'parent_ids':    [(6,0,maintask_id)],
                            'gap_category_id': gap_line.functionality.category and gap_line.functionality.category.id or False,
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
    _name = "gap_analysis.line"
    _inherit = "gap_analysis.line"
    
    _columns = {   
        'to_project': fields.boolean('Add to project ?', help='Specify whether this functionality must create a task or not when you generate a project.'),
    }
    _defaults = {
        'to_project': lambda *a: True,
    }    
gap_analysis_line()



class openerp_module(osv.osv):
    _name = "openerp_module"
    
    _columns = {
        'name':    fields.char('Name', size=128, required=True),
        'version': fields.char('Version', size=128),
        'note':    fields.text('Note'),
    }
openerp_module()



class project(osv.osv):
    _inherit = "project.project"
    _name = "project.project"
    
    _columns = {
        'gap_analysis_id': fields.many2one('gap_analysis', 'Gap Analysis'),
    }
project()


class project_task(osv.osv):
    _inherit = "project.task"
    _name = "project.task"
    
    def _get_parent_category(self, cr, uid, ids, fields, args, context=None):
        context = context or {}
        res = {}
        for task in self.browse(cr, uid, ids):
            res[task.id] = task.gap_category_id and task.gap_category_id.parent_id.id or False
        return res
    
    def _task_to_update_after_category_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('project.task').search(cr, uid, [('gap_category_id', 'in', ids)]) or []
    
    def _get_child_tasks(self, cr, uid, ids, context=None):
        if type(ids) != type([]):
            ids = [ids]
        cr.execute("SELECT DISTINCT parent_id FROM project_task_parent_rel WHERE task_id in %s", (tuple(ids),))
        task_ids = filter(None, map(lambda x:x[0], cr.fetchall())) or []
        return task_ids
    
    def _get_child_hours(self, cr, uid, ids, field_names, args, context=None):
        result = {}
        for task in self.browse(cr, uid, ids, context=context):
            res = {}
            child_org_planned_hours = 0.0
            child_planned_hours     = 0.0
            child_remaining_hours   = 0.0
            
            for child in task.child_ids:
                child_org_planned_hours += child.org_planned_hours
                child_planned_hours     += child.planned_hours
                child_remaining_hours   += child.remaining_hours
            
            res['child_org_planned_hours'] = child_org_planned_hours
            res['child_planned_hours']     = child_planned_hours
            res['child_remaining_hours']   = child_remaining_hours
            result[task.id] = res
        return result
    
#    def onchange_planned(self, cr, uid, ids, planned = 0.0, effective = 0.0):
#        return {'value':{'remaining_hours': planned - effective, 'org_planned_hours':planned}}
    
    _columns = {
        'child_org_planned_hours': fields.function(_get_child_hours, string='Child Original Planned Hours', multi='child_hours', help="Computed using the sum of the child tasks Original planned hours.",
            store = {
                'project.task': (_get_child_tasks, ['org_planned_hours','planned_hours'], 10),
            }),
        'child_planned_hours':   fields.function(_get_child_hours, string='Child Planned Hours', multi='child_hours', help="Computed using the sum of the child tasks planned hours.",
            store = {
                'project.task': (_get_child_tasks, ['planned_hours','remaining_hours'], 10),
            }),
        'child_remaining_hours': fields.function(_get_child_hours, string='Child Remaining Hours', multi='child_hours', help="Computed using the sum of the child tasks work done.",
            store = {
                'project.task': (_get_child_tasks, ['planned_hours','remaining_hours'], 10),
            }),
        
        'module_id': fields.many2one('openerp_module', 'Module', select=True),
        'gap_category_id': fields.many2one('gap_analysis.functionality.category','Category', select=True),
        'parent_category': fields.function(_get_parent_category, method=True, type='many2one', obj='gap_analysis.functionality.category', string='Parent Category', store={'project.task': (lambda self, cr, uid, ids, context: ids, ['gap_category_id'], 10), 'gap_analysis.functionality.category': (_task_to_update_after_category_change, ['parent_id'], 10),}),
        'gap_line_id': fields.many2one('gap_analysis.line', 'Gap Analysis Line', select=True),
        'code_gap': fields.char('Code in Gap', size=6),
        'to_report': fields.boolean('Report to customer'),
        'org_planned_hours': fields.float('Original Planned Hours', help='Original estimated time to do the task, usually set by the project manager when the task is in draft state.'),
    }
project_task()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: