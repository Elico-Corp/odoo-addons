# -*- coding: utf-8 -*-
# © 2011 Cubic ERP - Teradata SAC(http://cubicerp.com)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields

class select_line_range(osv.osv_memory):
    _name = 'select.line.range'

    _columns = {
        'dts_id' : fields.many2one('delivery.time', 'Time', required=True, domain=[('type', '=', 'dts')]),
            }

    def show(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids)[0]
        route_obj = self.pool.get('delivery.route')
        route_ids = route_obj.search(cr, uid, [
                    ('dts_id', '=', data.dts_id.id),
                    ], context=context)
        return {
                'type': 'ir.actions.act_window',
                'res_model':'delivery.route.line',
                'view_type':'tree',
                'view_mode':'kanban,form',
                # how to use domain "in" 
                'domain':'["|",("route_id","in",%s),("route_id","=",None)]' % str(route_ids),
                }

select_line_range()
