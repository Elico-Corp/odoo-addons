# -*- coding: utf-8 -*-
# © 2014 Elico Corp(https://www.elico-corp.com)
# © 2014 Yannick Gouin (yannick.gouin@elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import time
from openerp.report import report_sxw

class stock_inventory_move_elico(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(stock_inventory_move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
             'time': time,
             'qty_total':self._qty_total
        })

    def _qty_total(self, objects):
        total = 0.0
        uom = objects[0].product_uom.name
        for obj in objects:
            total += obj.product_qty
        return {'quantity':total,'uom':uom}

report_sxw.report_sxw(
    'report.stock.inventory.move.elico',
    'stock.inventory',
    'addons/stock_location_reports/report/stock_inventory_move.rml',
    parser=stock_inventory_move_elico,
    header='internal'
)

