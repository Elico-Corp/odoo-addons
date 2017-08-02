

from osv import osv, fields
from osv.osv import except_osv
from tools.translate import _

class line_create_wizard(osv.TransientModel):
    _name = 'gap_analysis.line_create_wizard'

    _columns = {
        'gap_id' : fields.many2one('gap_analysis', 'Gap Analysis', required=True),
        'tmpl' : fields.boolean('', help='This is used to control the gap_id domain presented in the wizard'),
    }


    def create_line(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        fct_fields     = [
                             'workloads',
                             'critical',
                             'testing',
                             'duration_wk',
                             'unknown_wk',
                         ]
        
        fct_rel_fields = [
                             'category',
                             'openerp_fct',
                             'effort',
                         ]

        line_pool   = self.pool.get('gap_analysis.line')
        fct_pool    = self.pool.get('gap_analysis.functionality')
        self_browse = self.browse(cr, uid, ids[0], context=context)

        # If adding to a template, make sure all the functionalities are also templates.
        if self_browse.gap_id.is_tmpl:
            tmpl_stats = fct_pool.read(cr, uid, context['active_ids'], ['is_tmpl','name'], context=context)
            if not all([tmpl_stat['is_tmpl'] for tmpl_stat in tmpl_stats]):
                non_tmpls = [tmpl_stat['name'] for tmpl_stat in tmpl_stats if not tmpl_stat['is_tmpl']]
                raise except_osv(
                                    _('Error: Non-template functionalities may not be added to a Gap Analysis Template.'),
                                    _('Please configure these functionalities accordingly and retry:\n\n%s') % ('\n\n'.join(non_tmpls))
                                )

        fct_defs    = fct_pool.read(cr, uid, context['active_ids'], fct_fields + fct_rel_fields, context=context)
        gap_id      = self_browse.gap_id.id
        new_params = {'gap_id' : gap_id}

        for fct_def in fct_defs:
            for rel_field in fct_rel_fields:
                fct_def[rel_field] = fct_def[rel_field] and fct_def[rel_field][0]

            if fct_def['workloads']:
                wkld_pool = self.pool.get('gap_analysis.workload')
                wkld_cps = []
                for wkld in fct_def['workloads']:
                    wkld_cp = wkld_pool.copy(cr, uid, wkld, {'fct_id' : False}, context=context)
                    wkld_cps.append(wkld_cp)
                fct_def['workloads'] = [(6, 0, wkld_cps)]

            new_params.update(functionality=fct_def['id'])

            fct_def.update(new_params)
            del fct_def['id']
            line_pool.create(cr, uid, fct_def, context=context)

        return {'type' : 'ir.actions.act_window_close'}


line_create_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
