# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import time
import netsvc
from osv import fields, osv
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _
import base64

import xlrd
from xlrd import open_workbook
import xlutils.copy


def getcell(rs, line, col, forceText=False):
        if not rs.cell(line, col).ctype in [0, 6]:
            if forceText and rs.cell(line, col).ctype in (2,3):
                return str(int(rs.cell_value(line, col)))
            else:
                return rs.cell_value(line, col)
        return None


def getfloat(str_float):
    try:
        if str_float:
            return float(str_float)
    except ValueError:
        pass
    return 0.0


def getint(str_int):
    try:
        if str_int:
            return int(str_int)
    except ValueError:
        pass
    return 0



class GapLineTemp(object):
    def __init__(self, gap_analysis, keep, functionality, function_desc, category, critical_level, phase, contributors, openerp_fct, basic_report, advan_report, basic_process, advan_process, basic_screen, advan_screen, basic_workflow, advan_workflow, acl, obj, calcul_field, basic_wizard, advan_wizard, effort, duration_wk, total_cost, total_analysis, total_dev, testing, training, project_mgmt):
        self.gap_analysis   = gap_analysis
        self.keep           = keep
        self.functionality  = functionality
        self.function_desc  = function_desc
        self.category       = category
        self.critical_level = critical_level or 0
        self.phase          = phase or '1'
        self.contributors   = contributors or ''
        self.openerp_fct    = openerp_fct or ''        
        self.basic_report   = (basic_report * 1)
        self.advan_report   = (advan_report * 1)
        self.basic_process  = (basic_process * 1)
        self.advan_process  = (advan_process * 1)
        self.basic_screen   = (basic_screen * 1)
        self.advan_screen   = (advan_screen * 1)
        self.basic_workflow = (basic_workflow * 1)
        self.advan_workflow = (advan_workflow * 1)
        self.acl            = (acl * 1)
        self.obj            = (obj * 1)
        self.calcul_field   = (calcul_field * 1)
        self.basic_wizard   = (basic_wizard * 1)
        self.advan_wizard   = (advan_wizard * 1)
        self.effort         = effort
        self.testing        = testing
        self.training       = training
        self.project_mgmt   = project_mgmt
        self.duration_wk    = (duration_wk * 1)
        self.total_cost     = total_cost
        self.total_analysis = total_analysis
        self.total_dev      = total_dev



class gap_analysis_import_xls(osv.osv_memory):
    _name='gap_analysis.import_xls'
    
    _columns = {
        'import_file': fields.binary('.XLS file', required=True),
    }

    
    def import_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        (data,)     = self.browse(cr, uid, ids, context=context)
        import_file = base64.b64decode(data.import_file)

        
        def create_workload(cr, uid, g_wkld_pool, wkld_type, gap_line_id, duration):
            wkld_vals = {
                'gap_line_id': gap_line_id,
                'fct_id':      False,
                'type':        wkld_type,
                'duration':    duration,
            }
            return g_wkld_pool.create(cr, uid, wkld_vals)
            
            
        def retrieve_gap_analysis(filecontents):
            warning = ''
            g_cat_pool = self.pool.get('gap_analysis.functionality.category')
            gap_lines_entries = {}
            rb = open_workbook(file_contents=filecontents,formatting_info=True, encoding_override="utf-8")
            
            for rs in rb.sheets():    
                for line in range(3, rs.nrows):
                    try:
                        keep = getcell(rs, line,  1)
                        if keep in [1, 'keep', 'Keep']:
                            keep = True
                        else:
                            keep = False
                        
                        gap_analysis   = rs.name.strip()
                        category       = getcell(rs, line, 2, forceText=True)
                        functionality  = getcell(rs, line, 3, forceText=True)
                        function_desc  = getcell(rs, line, 4, forceText=True)
                        critical_level = getint(getcell(rs, line, 5))
                        phase          = getcell(rs, line, 6)
                        contributors   = getcell(rs, line, 7, forceText=True)
                        openerp_fct    = getcell(rs, line, 8, forceText=True)
                        basic_report   = getfloat(getcell(rs, line, 9))
                        advan_report   = getfloat(getcell(rs, line, 10))
                        basic_process  = getfloat(getcell(rs, line,11))
                        advan_process  = getfloat(getcell(rs, line,12))
                        basic_screen   = getfloat(getcell(rs, line,13))
                        advan_screen   = getfloat(getcell(rs, line,14))
                        basic_workflow = getfloat(getcell(rs, line,15))
                        advan_workflow = getfloat(getcell(rs, line,16))
                        acl            = getfloat(getcell(rs, line,17))
                        obj            = getfloat(getcell(rs, line,18))
                        calcul_field   = getfloat(getcell(rs, line,19))
                        basic_wizard   = getfloat(getcell(rs, line,20))
                        advan_wizard   = getfloat(getcell(rs, line,21))
                        training       = getfloat(getcell(rs, line,22))
                        project_mgmt   = getfloat(getcell(rs, line,23))
                        effort         = getint(getcell(  rs, line,24))
                        duration_wk    = getfloat(getcell(rs, line,25))
                        testing        = getfloat(getcell(rs, line,26))
                        total_cost     = getfloat(getcell(rs, line,27))
                        total_analysis = getfloat(getcell(rs, line,28))
                        total_dev      = getfloat(getcell(rs, line,29))
                        
                        if functionality:
                            if category:
                                categ_ids = g_cat_pool.search(cr, uid, ['|',('name','ilike',category),('full_path','ilike',category)])
                                if categ_ids:
                                    category = categ_ids[0]
                            
                                    gap_line = GapLineTemp(gap_analysis, keep, functionality.strip(), function_desc, category, critical_level, phase, contributors, openerp_fct, basic_report, advan_report, basic_process, advan_process, basic_screen, advan_screen, basic_workflow, advan_workflow, acl, obj, calcul_field, basic_wizard, advan_wizard, effort, duration_wk, total_cost, total_analysis, total_dev, testing, training, project_mgmt)
                                    if gap_line:
                                        gap_lines_entries[rs.name.lower().strip() + str(line)] = gap_line
                                else:
                                    warning += 'The category ' + str(category) + ' does not exist in OpenERP. Please create it first, then upload you Gap analysis again.\n'
                            else:
                                warning += 'The category ' + str(category) + ' does not exist in OpenERP. Please create it first, then upload you Gap analysis again.\n'
                        else:
                            print(" ("+ str(line) +"), No functionality... ########################  .......")
                    except RuntimeError as error:
                        print(" ("+ str(line) +", "+ str(col) +"), didn't make it ########################  ......."+ str(error))
            
            if warning != '':
                raise osv.except_osv(_('Error'), warning)
                return []
            return gap_lines_entries

        gap_pool    = self.pool.get('gap_analysis')
        g_line_pool = self.pool.get('gap_analysis.line')
        g_fct_pool  = self.pool.get('gap_analysis.functionality')
        g_open_pool = self.pool.get('gap_analysis.openerp')
        effort_pool = self.pool.get('gap_analysis.effort')
        g_wkld_pool = self.pool.get('gap_analysis.workload')
        g_type_pool = self.pool.get('gap_analysis.workload.type')
        
        gap_lines = retrieve_gap_analysis(import_file)
        gap_dic   = {}
        wkld_dic  = {}
        
        # Get list of possible workload
        all_wkld = g_type_pool.search(cr, uid, [])
        for wkld in g_type_pool.browse(cr, uid, all_wkld):
            wkld_dic[wkld.code] = wkld.id
        
        for linenb, gap_line in gap_lines.items():
            # Check Gap Analysis
            if gap_line.gap_analysis not in gap_dic:
                gap_ids = gap_pool.search(cr, uid, [('name','=',gap_line.gap_analysis)])
                if not gap_ids:                
                    gap_id = gap_pool.create(cr, uid, {'name':gap_line.gap_analysis,})
                    print('Gap Import: Gap %s created (%s)'%(gap_line.gap_analysis,gap_id))
                else:
                    gap_id = gap_ids[0]
                    print('Gap Import: Gap %s found (%s)'%(gap_line.gap_analysis,gap_id))
                gap_dic[gap_line.gap_analysis] = gap_id
            
            
            # Check Functionality
            fct_ids = g_fct_pool.search(cr, uid, [('name','ilike',gap_line.functionality)])
	    if True:
#            if not fct_ids:
                # Create Functionality
                fct_id = g_fct_pool.create(cr, uid, {'name':gap_line.functionality,'description': gap_line.function_desc,'category':gap_line.category,})
                print('Gap Import: Fct %s created (%s)'%(gap_line.functionality,fct_id))
            else:
                fct_id = fct_ids[0]
                print('Gap Import: Fct %s found (%s)'%(gap_line.functionality,fct_id))
            
            
            # Check OpenERP Features
            open_id = False
            if gap_line.openerp_fct:
                open_ids = g_open_pool.search(cr, uid, [('name','=',gap_line.openerp_fct)])
                if not open_ids:
                    open_id = g_open_pool.create(cr, uid, {'name':gap_line.openerp_fct,})
                    print('Gap Import: OpenERP %s created (%s)'%(gap_line.openerp_fct,open_id))
                else:
                    open_id = open_ids[0]
                    print('Gap Import: OpenERP %s found (%s)'%(gap_line.openerp_fct,open_id))
            
            # Check Effort
            effort_id = False
            effort_ids = effort_pool.search(cr, uid, [('name','=',gap_line.effort)])
            if effort_ids:
                effort_id = effort_ids[0]
            
            # Create Gap Analysis Line
            if gap_line.duration_wk:
                unknown_wk = True
            else:
                unknown_wk = False
            
            g_line_vals = {
                'gap_id':        gap_dic[gap_line.gap_analysis],
                'functionality': fct_id,
                'workloads':     [],
                'openerp_fct':   open_id,
                'contributors':  gap_line.contributors,
                'keep':          gap_line.keep,
                'phase':         gap_line.phase,
                'critical':      gap_line.critical_level,   
                'effort':        effort_id,
                'duration_wk':   gap_line.duration_wk,
                'unknown_wk':    unknown_wk,
                'testing':       gap_line.testing,
                'category':      gap_line.category,
            }
            g_line_id = g_line_pool.create(cr, uid, g_line_vals)
            
            # Create Workloads
            if gap_line.basic_report > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasRep'], g_line_id, gap_line.basic_report)
            if gap_line.advan_report > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvRep'], g_line_id, gap_line.advan_report)
            if gap_line.basic_process > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasPro'], g_line_id, gap_line.basic_process)
            if gap_line.advan_process > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvPro'], g_line_id, gap_line.advan_process)
            if gap_line.basic_screen > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasScr'], g_line_id, gap_line.basic_screen)
            if gap_line.advan_screen > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvScr'], g_line_id, gap_line.advan_screen)
            if gap_line.basic_workflow > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasWkf'], g_line_id, gap_line.basic_workflow)
            if gap_line.advan_workflow > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvWkf'], g_line_id, gap_line.advan_workflow)
            if gap_line.acl > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Acl'], g_line_id, gap_line.acl)
            if gap_line.obj > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Obj'], g_line_id, gap_line.obj)
            if gap_line.calcul_field > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Cal'], g_line_id, gap_line.calcul_field)
            if gap_line.basic_wizard > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasWiz'], g_line_id, gap_line.basic_wizard)
            if gap_line.advan_wizard > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvWiz'], g_line_id, gap_line.advan_wizard)
            if gap_line.project_mgmt > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['PrjMan'], g_line_id, gap_line.project_mgmt)
            if gap_line.training > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Train'], g_line_id, gap_line.training)
        
        return {'type': 'ir.actions.act_window_close'}

gap_analysis_import_xls()




class gap_analysis_import_fct_xls(osv.osv_memory):
    _name='gap_analysis.import_fct_xls'
    
    _columns = {
        'import_file': fields.binary('.XLS file', required=True),
    }

    
    def import_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        (data,)     = self.browse(cr, uid, ids, context=context)
        import_file = base64.b64decode(data.import_file)

        
        def create_workload(cr, uid, g_wkld_pool, wkld_type, fct_id, duration):
            wkld_vals = {
                'gap_line_id': False,
                'fct_id':      fct_id,
                'type':        wkld_type,
                'duration':    duration,
            }
            return g_wkld_pool.create(cr, uid, wkld_vals)
            
            
        def retrieve_gap_analysis_fct(filecontents):
            fct_entries = {}
            g_cat_pool = self.pool.get('gap_analysis.functionality.category')
            warning = ''
            rb = open_workbook(file_contents=filecontents,formatting_info=True, encoding_override="utf-8")
            
            for rs in rb.sheets():    
                for line in range(3, rs.nrows):
                    try:
                        keep = False                        
                        gap_analysis   = rs.name.strip()
                        functionality  = getcell(rs, line, 0, forceText=True)
                        function_desc  = getcell(rs, line, 1, forceText=True)
                        critical_level = getint(getcell(rs, line, 2))
                        phase          = False
                        contributors   = ''
                        openerp_fct    = getcell(rs, line, 3, forceText=True)
                        basic_report   = getfloat(getcell(rs, line, 4))
                        advan_report   = getfloat(getcell(rs, line, 5))
                        basic_process  = getfloat(getcell(rs, line, 6))
                        advan_process  = getfloat(getcell(rs, line, 7))
                        basic_screen   = getfloat(getcell(rs, line, 8))
                        advan_screen   = getfloat(getcell(rs, line, 9))
                        basic_workflow = getfloat(getcell(rs, line,10))
                        advan_workflow = getfloat(getcell(rs, line,11))
                        acl            = getfloat(getcell(rs, line,12))
                        obj            = getfloat(getcell(rs, line,13))
                        calcul_field   = getfloat(getcell(rs, line,14))
                        basic_wizard   = getfloat(getcell(rs, line,15))
                        advan_wizard   = getfloat(getcell(rs, line,16))
                        training       = getfloat(getcell(rs, line,17))
                        project_mgmt   = getfloat(getcell(rs, line,18))
                        effort         = getint(getcell(  rs, line,19))
                        duration_wk    = getfloat(getcell(rs, line,20))
                        testing        = getfloat(getcell(rs, line,21))
                        total_cost     = getfloat(getcell(rs, line,22))
                        total_analysis = getfloat(getcell(rs, line,23))
                        total_dev      = getfloat(getcell(rs, line,24))
                        category       = getcell(rs, line, 25, forceText=True)
                        
                        if functionality:
                            if category:
                                categ_ids = g_cat_pool.search(cr, uid, ['|',('name','ilike',category),('full_path','ilike',category)])
                                if categ_ids:
                                    category = categ_ids[0]
                                    one_fct = GapLineTemp(gap_analysis, keep, functionality.strip(), function_desc, category, critical_level, phase, contributors, openerp_fct, basic_report, advan_report, basic_process, advan_process, basic_screen, advan_screen, basic_workflow, advan_workflow, acl, obj, calcul_field, basic_wizard, advan_wizard, effort, duration_wk, total_cost, total_analysis, total_dev, testing, training, project_mgmt)
                                    if one_fct:
                                        fct_entries[rs.name.lower().strip() + str(line)] = one_fct
                                else:
                                    warning += 'The category ' + str(category) + ' dont exist in OpenERP. Please create it first, then upload you Gap analysis.\n'
                            else:
                                warning += 'The category ' + str(category) + ' dont exist in OpenERP. Please create it first, then upload you Gap analysis.\n'
                        else:
                            print(" ("+ str(line) +"), No functionality... ########################  .......")
                    except RuntimeError as error:
                        print(" ("+ str(line) +", "+ str(col) +"), didn't make it ########################  ......."+ str(error))
            
            if warning != '':
                raise osv.except_osv(_('Error'), warning)
                return []
            return fct_entries

        
        g_fct_pool  = self.pool.get('gap_analysis.functionality')
        g_open_pool = self.pool.get('gap_analysis.openerp')
        effort_pool = self.pool.get('gap_analysis.effort')
        g_wkld_pool = self.pool.get('gap_analysis.workload')
        g_type_pool = self.pool.get('gap_analysis.workload.type')
        
        fct_entries = retrieve_gap_analysis_fct(import_file)
        gap_dic   = {}
        wkld_dic  = {}
        
        # Get list of possible workload
        all_wkld = g_type_pool.search(cr, uid, [])
        for wkld in g_type_pool.browse(cr, uid, all_wkld):
            wkld_dic[wkld.code] = wkld.id
        
        for linenb, one_fct in fct_entries.items():
            # Check OpenERP Features
            open_id = False
            if one_fct.openerp_fct:
                open_ids = g_open_pool.search(cr, uid, [('name','=',one_fct.openerp_fct)])
                if not open_ids:
                    open_id = g_open_pool.create(cr, uid, {'name':one_fct.openerp_fct,})
                    print('Gap Import: OpenERP %s created (%s)'%(one_fct.openerp_fct,open_id))
                else:
                    open_id = open_ids[0]
                    print('Gap Import: OpenERP %s found (%s)'%(one_fct.openerp_fct,open_id))
            
            # Check Effort
            effort_id = False
            effort_ids = effort_pool.search(cr, uid, [('name','=',one_fct.effort)])
            if effort_ids:
                effort_id = effort_ids[0]
            
            if one_fct.duration_wk:
                unknown_wk = True
            else:
                unknown_wk = False
            
            
            # Check Functionality
            fct_ids = g_fct_pool.search(cr, uid, [('name','ilike',one_fct.functionality)])
            if not fct_ids:
                # Create Functionality
                fct_vals = {
                    'name':        one_fct.functionality,
                    'description': one_fct.function_desc,
                    'category':    one_fct.category,
                    'workloads':   [],
                    'openerp_fct': open_id,
                    'critical':    one_fct.critical_level,   
                    'effort':      effort_id,
                    'duration_wk': one_fct.duration_wk,
                    'unknown_wk':  unknown_wk,
                    'is_tmpl':     True,
                    'proposed':    False,
                    'testing':     gap_line.testing,
                }
                fct_id = g_fct_pool.create(cr, uid, fct_vals)
                print('Gap Import: Fct %s created (%s)'%(one_fct.functionality,fct_id))
            
            else:
                fct_id = fct_ids[0]
                # Update Functionality
                fct_vals = {
                    'description': one_fct.function_desc,
                    'workloads':   [],
                    'openerp_fct': open_id,
                    'critical':    one_fct.critical_level,   
                    'effort':      effort_id,
                    'duration_wk': one_fct.duration_wk,
                    'unknown_wk':  unknown_wk,
                    'is_tmpl':     True,
                    'proposed':    False,
                    'testing':     gap_line.testing,
                }
                g_fct_pool.write(cr, uid, [fct_id], fct_vals)
                print('Gap Import: Fct %s found (%s) (%s)'%(one_fct.functionality,fct_id,fct_vals))
                
            # Create Workloads
            if one_fct.basic_report > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasRep'], fct_id, one_fct.basic_report)
            if one_fct.advan_report > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvRep'], fct_id, one_fct.advan_report)
            if one_fct.basic_process > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasPro'], fct_id, one_fct.basic_process)
            if one_fct.advan_process > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvPro'], fct_id, one_fct.advan_process)
            if one_fct.basic_screen > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasScr'], fct_id, one_fct.basic_screen)
            if one_fct.advan_screen > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvScr'], fct_id, one_fct.advan_screen)
            if one_fct.basic_workflow > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasWkf'], fct_id, one_fct.basic_workflow)
            if one_fct.advan_workflow > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvWkf'], fct_id, one_fct.advan_workflow)
            if one_fct.acl > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Acl'], fct_id, one_fct.acl)
            if one_fct.obj > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Obj'], fct_id, one_fct.obj)
            if one_fct.calcul_field > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Cal'], fct_id, one_fct.calcul_field)
            if one_fct.basic_wizard > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['BasWiz'], fct_id, one_fct.basic_wizard)
            if one_fct.advan_wizard > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['AdvWiz'], fct_id, one_fct.advan_wizard)
            if one_fct.project_mgmt > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['PrjMan'], fct_id, one_fct.project_mgmt)
            if one_fct.training > 0:
                g_wkld_id = create_workload(cr, uid, g_wkld_pool, wkld_dic['Train'], fct_id, one_fct.training)
            
        return {'type': 'ir.actions.act_window_close'}

gap_analysis_import_fct_xls()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
