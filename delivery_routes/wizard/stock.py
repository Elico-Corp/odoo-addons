# -*- coding: utf-8 -*-
# © 2011 Cubic ERP - Teradata SAC(http://cubicerp.com)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields

class arrange_time(osv.osv_memory):
    _name = 'arrange.time'

    _columns = {
        'dts_id' : fields.many2one('delivery.time', 'Time', required=True, domain=[('type', '=', 'dts')]),
    }

    def confirm_add(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids)[0]
        picking_ids = context['active_ids']
        
        picking_obj = self.pool.get('stock.picking')
        line_obj = self.pool.get('delivery.route.line')
        #TODO give warning to limit the rewrite!!
        picking_obj.write(cr, uid, picking_ids, {'dts_id':data.dts_id.id})
        for picking_id in picking_ids:
            line_obj.create(cr, uid, {'picking_id':picking_id}, context=context)
        return {
                'type': 'ir.actions.act_window_close',
                }

arrange_time()
