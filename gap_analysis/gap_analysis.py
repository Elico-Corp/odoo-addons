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


class gap_analysis_effort(osv.osv):
    _name = "gap_analysis.effort"
    _description = "Gap Analysis Efforts"
    
    _columns = {
        'name':     fields.char('Effort', size=4, required=True,),
        'unknown':  fields.boolean('Undefined duration ?', help='If checked, when this effort is used, the user would have to specify the duration manually.'),
        'duration': fields.float('Duration (hour)', help='Duration in hour for this effort.', required=True,),
    }
    
    def onchange_unknown(self, cr, uid, ids, unknown):
        val = {}
        val['unknown'] = unknown
        if not unknown:
            val['duration'] = 0.0
        return {'value': val}
    
    _order = 'name'
gap_analysis_effort()


class gap_analysis_workload_type(osv.osv):
    _name = "gap_analysis.workload.type"
    _description = "Gap Analysis Workload Type"
    
    _columns = {
        'name':     fields.char('Name', size=64, required=True, translate=True),
        'category': fields.selection([('Functional Analysis','Functional'), ('Technical Analysis','Technical')], 'Analysis', required=True,),
        'code':     fields.char('Code for Report', size=8, required=True, translate=True, help="Set the code if name is too long (eg: in reports)."),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of workload type."),
        'duration': fields.float('Duration (hour)', help='Default duration in hour for this type of workload.', required=True,),
    }
    _defaults = {
        'sequence': lambda *a: 10,
        'category': lambda *a: 'Functional Analysis',
        'duration': lambda *a: 4,
    }
    _order = 'sequence'
gap_analysis_workload_type()



class gap_analysis_workload(osv.osv):
    _name = "gap_analysis.workload"
    _description = "Gap Analysis Workload"
    
    _columns = {
        'gap_line_id': fields.many2one('gap_analysis.line', 'Gap-analysis Line', ondelete='cascade', select=True, readonly=True),
        'fct_id':      fields.many2one('gap_analysis.functionality', 'Gap-analysis Functionality Template', ondelete='cascade', select=True, readonly=True),
        'type':        fields.many2one('gap_analysis.workload.type', 'Type', required=True, select=True),
        'duration':    fields.float('Duration (hour)', help='Duration in hour for this task.', required=True,),
    }
    
    def onchange_type_id(self, cr, uid, ids, type_id):
        val = {}
        my_type = self.pool.get('gap_analysis.workload.type').browse(cr, uid, type_id)
        val['duration'] = my_type.duration
        return {'value': val}


gap_analysis_workload()



class gap_analysis_functionality_category(osv.osv):
    _inherit = "product.category"
    _name = "gap_analysis.functionality.category"
    _description = "Gap Analysis Functionality Categories"
    
    
    def _category_to_update(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('gap_analysis.functionality.category').search(cr, uid, [], order='parent_left') or []
    
    def _name_get_full_path(self, cursor, uid, ids, fields, arg, context=None):
        result = {}
        for category in self.browse(cursor, uid, ids):
            full_path = ''
            current_category = category
            while current_category:
                if full_path=='':
                    full_path = ustr(current_category.name)
                else:
                    full_path = ustr(current_category.name) + ' / ' + full_path
                current_category = current_category.parent_id or False
            result[category.id] = full_path
        return result
    
    
    _columns = {
        'parent_id':   fields.many2one('gap_analysis.functionality.category','Parent Category', select=True, ondelete='cascade'),
        'child_id':    fields.one2many('gap_analysis.functionality.category', 'parent_id', string='Child Categories'),
        'code':        fields.char('Code', size=8, required=True, help="Use for functionality sequencing."),
        'full_path':   fields.function(_name_get_full_path, type="char", method=True, size=2048, store={'gap_analysis.functionality.category': (_category_to_update, ['name','parent_id'], 10)}, string='Name'),
    }
    
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from gap_analysis_functionality_category where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive categories.', ['parent_id'])
    ]
    
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_left'
gap_analysis_functionality_category()



class gap_analysis_functionality(osv.osv):
    _name = "gap_analysis.functionality"
    _description = "Gap Analysis Functionalities"
    

    def _search_ga_lines(self, cr, uid, ids, field_names, arg=None, context=None, tmpl=False):
        if context is None:
            context = {}

        ga_obj      = self.pool.get('gap_analysis')
        ga_line_obj = self.pool.get('gap_analysis.line')
        func_obj    = self.pool.get('gap_analysis.functionality')

        line_ids = ga_line_obj.search(cr, uid, [('functionality','=', ids[0])], context=context)

        lids_to_gids = {}
        tmpl_lids = []
        ga_obj = self.pool.get('gap_analysis')
        gap_ids = ga_line_obj.read(cr, uid, line_ids, ['gap_id'], context=context)

        for gap_id in gap_ids:
            lids_to_gids[gap_id['id']] = gap_id['gap_id'][0]

        tmpl_checks = ga_obj.read(cr, uid, [gid['gap_id'][0] for gid in gap_ids], ['is_tmpl'], context=context)
        gids_to_checks = dict(zip([c['id'] for c in tmpl_checks], [c['is_tmpl'] == tmpl for c in tmpl_checks]))

        for lid in lids_to_gids.keys():
            if gids_to_checks[lids_to_gids[lid]]:
                tmpl_lids.append(lid)

        return {ids[0] : [l for l in line_ids if l in tmpl_lids]}


    def _search_ga_tmpl_lines(self, cr, uid, ids, field_names, arg=None, context=None):
        return self._search_ga_lines(cr, uid, ids, field_names, arg=arg, context=context, tmpl=True)


    def _search_ga_non_tmpl_lines(self, cr, uid, ids, field_names, arg=None, context=None):
        return self._search_ga_lines(cr, uid, ids, field_names, arg=arg, context=context, tmpl=False)


    _columns = {
        'name':          fields.char('Functionality', size=256, required=True, translate=True),
        'description':   fields.text('Description'),
        'category':      fields.many2one('gap_analysis.functionality.category', 'Category', required=True, select=True),
        'is_tmpl':       fields.boolean('Template ?', help='This Functionality is a Template ?'),
        'proposed':      fields.boolean('Propose as template ?'),
        #### Default values (Templating) ####
        'workloads':     fields.one2many('gap_analysis.workload', 'fct_id', 'Default Workloads'),
        'openerp_fct':   fields.many2one('gap_analysis.openerp', 'Default OpenERP feature', select=True),
        'critical':      fields.integer('Default Critical Level', help='Indicator to specify the importance of this functionality in the project.'),
        'testing':       fields.float('Test (hour)'),
        'effort':        fields.many2one('gap_analysis.effort', 'Default Effort', help="Development Effort for this functionality."),
        'duration_wk':   fields.float('Default Duration (hour)', help='Since this effort has no pre-defined duration, you must set one.'),
        'unknown_wk':    fields.boolean('Must set the duration manually ? (Default)',),
        'ga_lines':      fields.function(_search_ga_non_tmpl_lines, type='one2many', relation='gap_analysis.line', method=True, string='Gap Analysis Lines'),
        'ga_tmpl_lines': fields.function(_search_ga_tmpl_lines, type='one2many', relation='gap_analysis.line', method=True, string='Gap Analysis Template Lines'),
    }


    def open_line_wizard(self, cr, uid, ids, context=None):
        if context is None:
            context={}

        title = context.get('default_tmpl', False) and 'Create New Template Entry' or 'Create New Entry'

        return {
                   'type' : 'ir.actions.act_window',
                   'name' : title,
                   'res_model': 'gap_analysis.line_create_wizard',
                   'view_type' : 'form',
                   'view_mode' : 'form',
                   'target' : 'new',
                   'context' : context,
               }
    

    def onchange_is_tmpl(self, cr, uid, ids, is_tmpl, context=None):
        if context is None:
            context = {}
        
        if not is_tmpl or not len(ids):
            return {}

        ga_line_pool = self.pool.get('gap_analysis.line')
        related_lines = ga_line_pool.search(cr, uid, [('functionality','=',ids[0])], context=context)

        if not related_lines:
            return {}

        source_line = max(related_lines)
        fields_to_read = ['workloads', 'openerp_fct', 'critical', 'testing', 'effort', 'duration_wk', 'unknown_wk']
        val = ga_line_pool.read(cr, uid, source_line, fields_to_read, context=context)

        if val.get('workloads', False):
            wkld_pool = self.pool.get('gap_analysis.workload')
            new_wklds = []
            for wkld in val['workloads']:
                wkld_data = wkld_pool.read(cr, uid, wkld, ['type', 'duration'])
                new_wklds.append({'fct_id' : ids[0], 'gap_line_id' : False, 'type' : wkld_data['type'][0], 'duration' : wkld_data['duration']})
            val['workloads'] = new_wklds

        return {'value' : val}
        

    def onchange_effort_id(self, cr, uid, ids, effort_id, unknown_wk):
        val = {}
        if effort_id:
            my_effort = self.pool.get('gap_analysis.effort').browse(cr, uid, effort_id)
            val['unknown_wk'] = my_effort.unknown
        else:
            val['unknown_wk'] = False
        return {'value': val}
    
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'is_tmpl' in vals and vals['is_tmpl'] == True:
            vals['proposed'] = False
        res = super(gap_analysis_functionality, self).write(cr, uid, ids, vals, context=context)
        if res:
            id_list = isinstance(ids, list) and ids[:] or [ids]
            line_pool = self.pool.get('gap_analysis.line')
            for fid in id_list:
                lids = line_pool.search(cr, uid, [('gap_id.is_tmpl','=',True),('functionality','=',fid)], context=context)
                line_pool.set_values_by_fct(cr, uid, lids, fid, context=context)
            
        return res
    
gap_analysis_functionality()


class gap_analysis_openerp(osv.osv):
    _name = "gap_analysis.openerp"
    _description = "Gap Analysis OpenERP features"
    
    _columns = {
        'name':       fields.char('OpenERP feature', size=256, required=True, translate=True),
    } 
gap_analysis_openerp()


class gap_analysis(osv.osv):
    _name = "gap_analysis"
    _description = "Gap Analysis"
    
    def _estimated_time_cost(self, cursor, uid, ids, fields, arg, context=None):
        result = {}
        for gap in self.browse(cursor, uid, ids):
            res = {}
            res['estimated_time'] = 0.0
            res['estimated_cost'] = 0.0
            
            for gap_line in gap.gap_lines:
                if gap_line.keep:
                    res['estimated_time'] += gap_line.total_time
                    res['estimated_cost'] += gap_line.total_cost
                
            result[gap.id] = res
        return result
    
    
    def _sorted_distinct_workloads(self, cursor, uid, ids, arg, context=None):
        result = {}
        for gap in self.browse(cursor, uid, ids):
            types = []
            line_ids = [l.id for l in gap.gap_lines]
            if line_ids:        
                cursor.execute("SELECT id, code FROM gap_analysis_workload_type T WHERE id in (SELECT DISTINCT(W.type) FROM gap_analysis_workload W WHERE W.gap_line_id IN %s) ORDER BY T.sequence ASC",(tuple(line_ids),))
                types = cursor.fetchall()
        return types
        
    
    def button_dummy(self, cr, uid, ids, context=None):
        gapline_pool = self.pool.get('gap_analysis.line')
        gap_cat_pool = self.pool.get('gap_analysis.functionality.category')
        if type(ids) != type([]):
            ids = [ids]
        
        for gap_id in ids:
            cr.execute("SELECT DISTINCT c.code FROM gap_analysis_line l, gap_analysis_functionality_category c WHERE l.category=c.id AND l.gap_id = %s",(gap_id,))
            categ_codes = map(lambda x: x[0], cr.fetchall()) or []
            
            for code in categ_codes:
                idx = 1
                seq = 999
                
                cr.execute("SELECT id FROM gap_analysis_functionality_category WHERE id IN (SELECT DISTINCT c.id FROM gap_analysis_line l, gap_analysis_functionality_category c WHERE l.category=c.id AND c.code = %s AND l.gap_id = %s) ORDER BY parent_left",(code, gap_id,))
                categ_ids = map(lambda x: x[0], cr.fetchall()) or []
                
                for categ in gap_cat_pool.browse(cr, uid, categ_ids):
                    current_categ = categ
                    seq = ''
                    while current_categ:
                        seq = str(current_categ.sequence) + seq
                        current_categ = current_categ.parent_id or False
                    
                    line_ids = gapline_pool.search(cr, uid, [('category','=',categ.id),('gap_id','=',gap_id)], order='critical desc, effort asc') or []
                    for line_id in line_ids:
                        code_line = code
                        code_line += str(idx).rjust(3, '0')
                        gapline_pool.write(cr, uid, [line_id], {'code':code_line,'seq':seq})
                        idx += 1
        return True
    
    
    def import_from_tmpl(self, cr, uid, ids, context=None):
        return {
            'name': _('Import from Template'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'gap_analysis.import_from_tmpl',
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': False,
        }
    
    
    def _get_lines(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('gap_analysis.line').browse(cr, uid, ids, context=context):
            result[line.gap_id.id] = True
        return result.keys()
    
    
    def action_change(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
            self.write(cr, uid, [o.id], {'state':'draft', 'date_confirm': False})
        return True
    
    def action_done(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
            self.write(cr, uid, [o.id], {'state': 'done', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
            self.write(cr, uid, [o.id], {'state': 'cancel'})
        return True
        
    
    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Warning'), _("Copying a Gap Analysis is currently not allowed."))
        return False
    
    
    def onchange_project_id(self, cr, uid, ids, project_id):
        val = {}
        my_project = self.pool.get('project.project').browse(cr, uid, project_id)
        if my_project.partner_id:
            val['partner_id'] = my_project.partner_id.id
        return {'value': val}
    
    
    _columns = {
        'reference':      fields.char('Reference', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}, select=True),
        'name':           fields.char('Name', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state':          fields.selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', readonly=True, help="Gives the state of the gap-analysis.", select=True),
        'note':           fields.text('Note'),
        'date_create':    fields.datetime('Creation Date', readonly=True, select=True, help="Date on which the gap-analysis is created."),
        'date_confirm':   fields.date('Confirmation Date', readonly=True, select=True, help="Date on which the gap-analysis is confirmed."),
        'user_id':        fields.many2one('res.users', 'Analyst', readonly=True, states={'draft': [('readonly', False)]}, select=True),
        'partner_id':     fields.many2one('res.partner', 'Customer', select=True, readonly=True, states={'draft': [('readonly', False)]}, ),
        'gap_lines':      fields.one2many('gap_analysis.line', 'gap_id', 'Functionalities', readonly=True, states={'draft': [('readonly', False)]}),
        'estimated_time': fields.function(_estimated_time_cost, type='float', multi="gapsums", string='Estimated Time', store = False),
        'estimated_cost': fields.function(_estimated_time_cost, type='float', multi="gapsums", string='Estimated Selling Price', store = False),
        'project_id':     fields.many2one('project.project', 'Project'),
        'partner_id':     fields.many2one('res.partner', 'Partner'),
        'is_tmpl':        fields.boolean('Template ?', help='This Gap Analysis is a Template ?'),
        'tech_cost':      fields.float('Technical Analysis Price', help='Default Price per hour for Technical Analysis.'),
        'func_cost':      fields.float('Functional Analysis Price', help='Default Price per hour for Functional Analysis.'),
        'dev_cost':       fields.float('Effort Price', help='Price per hour for Effort.'),
        
        'user_functional': fields.many2one('res.users', 'Default Functional Analyst'),
        'user_technical':  fields.many2one('res.users', 'Default Technical Analyst'),
        'user_dev':        fields.many2one('res.users', 'Default Developer'),
        'user_test':       fields.many2one('res.users', 'Default Tester'),
    }
    _defaults = {
        'state':       lambda *a: 'draft',
        'user_id':     lambda obj, cr, uid, context: uid,
        'user_functional': lambda obj, cr, uid, context: uid,
        'reference':   lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'gap_analysis'),
        'date_create': fields.date.context_today,
        'tech_cost':   lambda *a: 500.0,
        'func_cost':   lambda *a: 500.0,
        'dev_cost':    lambda *a: 250.0,
    }
    _sql_constraints = [
        ('reference_uniq', 'unique(reference)', 'Reference must be unique !'),
    ]
    _order = 'name desc'

gap_analysis()



class gap_analysis_line(osv.osv):
    _name = "gap_analysis.line"
    _description = "Gap-analysis Lines"

    def _estimated_line_time_cost(self, cursor, uid, ids, fields, arg, context=None):
        result = {}
        gap = False
        for gap_line in self.browse(cursor, uid, ids):
            res = {}
            res['total_time'] = 0
            res['total_cost'] = 0
            
            if not gap:
                gap = self.pool.get("gap_analysis").browse(cursor, uid, gap_line.gap_id.id)
                
            if gap_line.effort:           
                if gap_line.effort.unknown:
                    thistime = gap_line.duration_wk
                else:
                    thistime = gap_line.effort.duration
                
                res['total_time'] = thistime
                res['total_cost'] = (gap.dev_cost * thistime)
            
            for workload in gap_line.workloads:
                if workload.type.category == "Technical Analysis":
                    workload_cost = gap.tech_cost
                else:
                    workload_cost = gap.func_cost
                    
                res['total_time'] += workload.duration
                res['total_cost'] += (workload.duration * workload_cost)
            
            if gap_line.testing:
                res['total_time'] += gap_line.testing
                res['total_cost'] += (gap_line.testing * gap.tech_cost)
            
            result[gap_line.id] = res
        return result
    
    
    def _get_lines_from_workload(self, cr, uid, ids, context=None):
        result = {}
        for workload in self.pool.get('gap_analysis.workload').browse(cr, uid, ids, context=context):
            result[workload.gap_line_id.id] = True
        return result.keys()
    
    
    def _total_workloads(self, cursor, uid, ids, arg, context=None):
        result = {}
        for line in self.browse(cursor, uid, ids):
            amount = 0            
            for w in line.workloads:
                if w.type.id == arg:
                    amount += w.duration            
        return amount


    def set_values_by_fct(self, cr, uid, ids, fct_id, ret_fmt_onchange=False, context=None):
        vals = []
        fct_tmpl = self.pool.get('gap_analysis.functionality').browse(cr, uid, fct_id)
        id_list = isinstance(ids, list) and ids[:] or [ids]
        for lid in id_list:
            val = {}
            if fct_tmpl.effort:
                val['effort'] = fct_tmpl.effort.id
            if fct_tmpl.category:
                val['category'] = fct_tmpl.category.id
            if fct_tmpl.testing:
                val['testing'] = fct_tmpl.testing
            if fct_tmpl.unknown_wk:
                val['unknown_wk'] = fct_tmpl.unknown_wk
            if fct_tmpl.duration_wk:
                val['duration_wk'] = fct_tmpl.duration_wk
            if fct_tmpl.critical:
                val['critical'] = fct_tmpl.critical
            if fct_tmpl.openerp_fct:
                val['openerp_fct'] = fct_tmpl.openerp_fct.id
            if fct_tmpl.workloads:
                workload_pool = self.pool.get('gap_analysis.workload')
                my_workloads  = []
                for workload in fct_tmpl.workloads:
                    workload_vals = {'type':workload.type.id,'duration':workload.duration,}
                    if lid:
                        workload_vals['gap_line_id'] = lid
                    my_workloads.append(workload_vals)
                val['workloads'] = my_workloads
            if ret_fmt_onchange:
                vals.append(val)
            else:
                my_workloads = val.get('workloads', False)
                old_wkld_data = self.read(cr, uid, lid, ['workloads'], context=context)
                if old_wkld_data:
                    old_wklds = old_wkld_data['workloads']
                    wkld_unlink_tuples = [(2, wid) for wid in old_wklds]
                    val['workloads'] = wkld_unlink_tuples
                self.write(cr, uid, lid, val, context=context)
                if my_workloads:
                    wkld_tuples = []
                    for wkld in my_workloads:
                        wkld_tuples.append((0, 0, wkld))
                    self.write(cr, uid, lid, {'workloads':wkld_tuples}, context=context)
        return ret_fmt_onchange and vals or True

    
    def onchange_functionality_id(self, cr, uid, ids, fct_id, gap_id, context=None):
        ret = {}
        ids = isinstance(ids, list) and ids or [ids]
        val = self.set_values_by_fct(cr, uid, ids, fct_id, ret_fmt_onchange=True, context=context)
        ret.update({'value' : val[0]})

        if gap_id:
            ga_lines = self.search(cr, uid, [('gap_id','=',gap_id),('id','!=',ids[0])], context=context)
            if ga_lines:
                ga_fcts = self.read(cr, uid, ga_lines, ['functionality'], context=context)
                if fct_id in [fct['functionality'][0] for fct in ga_fcts]:
                    ret.update({'warning' : {
                                                'title'   : 'Warning: Functionality Duplication.',
                                                'message' : 'This functionality already exists within this Gap Analysis.',
                                            }})
        return ret
    
    
    def onchange_effort_id(self, cr, uid, ids, effort_id, unknown_wk):
        val = {}
        my_effort = self.pool.get('gap_analysis.effort').browse(cr, uid, effort_id)
        val['unknown_wk'] = my_effort.unknown
        return {'value': val}


    def _get_dummy_gap_is_tmpl(self, cr, uid, ids, fields, arg, context=None):
        gid = self.read(cr, uid, ids[0], ['gap_id'], context=context)['gap_id'][0]
        return {ids[0] : self.pool.get('gap_analysis').read(cr, uid, gid, ['is_tmpl'], context=context)['is_tmpl']}


    _columns = {
        'gap_id':        fields.many2one('gap_analysis', 'Gap-analysis', required=True, ondelete='cascade', select=True, readonly=True),
        'seq':           fields.char('Sequence', size=48),
        'code':          fields.char('Code', size=6),
        'functionality': fields.many2one('gap_analysis.functionality', 'Functionality', required=True, select=True),
        'category':      fields.many2one('gap_analysis.functionality.category', 'Category', required=True, select=True),
        'workloads':     fields.one2many('gap_analysis.workload', 'gap_line_id', 'Workloads'),
        'total_time':    fields.function(_estimated_line_time_cost, method=True, type='float', multi=True, string='Estimated Time', store = {'gap_analysis.line': (lambda self, cr, uid, ids, c={}: ids, ['testing','workloads','duration_wk','effort','unknown_wk'], 10),'gap_analysis.workload': (_get_lines_from_workload, ['workload', 'duration'], 10),}),
        'total_cost':    fields.function(_estimated_line_time_cost, method=True, type='float', multi=True, string='Estimated Selling Price', store = {'gap_analysis.line': (lambda self, cr, uid, ids, c={}: ids, ['testing','workloads','duration_wk','effort','unknown_wk'], 10),'gap_analysis.workload': (_get_lines_from_workload, ['workload', 'duration'], 10),}),
        'openerp_fct':   fields.many2one('gap_analysis.openerp', 'OpenERP feature', select=True),
        'contributors':  fields.char('Contributor', size=256, help='Who is/are your main contact(s) to define this functionality.'),
        'keep':          fields.boolean('Keep ?', help='Keep the functionality in the Gap Analysis. If unchecked, the functionality will be print in the report but not used for the price calculation.'),
        'critical':      fields.integer('Critical Level', help='Indicator to specify the importance of this functionality in the project.'),
        'testing':       fields.float('Test (hour)'),   
        'effort':        fields.many2one('gap_analysis.effort', 'Effort', help="Development Effort for this functionality."),
        'duration_wk':   fields.float('Duration (hour)', help='Since this effort has no pre-defined duration, you must set one.'),
        'unknown_wk':    fields.boolean('Must set the duration manually ?',),
        'dummy_gap_is_tmpl': fields.function(_get_dummy_gap_is_tmpl, type='boolean', name='dummy_gap_is_tmpl', method=True),
    }
    _defaults = {
        'unknown_wk':  lambda *a: False,
        'keep':        lambda *a: True,
        'critical':    lambda *a: 1,
    }
    
    _order = 'seq asc, code asc'
    _rec_name = 'code'
    
gap_analysis_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
