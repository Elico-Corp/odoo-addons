# -*- coding: utf-8 -*-
# © 2014 Elico Corp(https://www.elico-corp.com)
# © 2014 Yannick Gouin (yannick.gouin@elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp import pooler
import time
from openerp.report import report_sxw

class lot_overview_all(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(lot_overview_all, self).__init__(cr, uid, name, context=context)
        self.price_total = 0.0
        self.grand_total = 0.0
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'price_total': self._price_total,
            'grand_total_price':self._grand_total,
        })

    def process(self, location_id):
        location_obj = pooler.get_pool(self.cr.dbname).get('stock.location')
        data = location_obj._product_get_all_report(self.cr, self.uid, [location_id])
        data['location_name'] = location_obj.read(self.cr, self.uid, [location_id], ['complete_name'])[0]['complete_name']
        self.price_total = 0.0
        self.price_total += data['total_price']
        self.grand_total += data['total_price']
        return [data]

    def _price_total(self):
        return self.price_total

    def _grand_total(self):
        return self.grand_total

report_sxw.report_sxw('report.lot.stock.overview_all2', 'stock.location', 'addons/stock_location_reports/report/lot_overview_all.rml', parser=lot_overview_all, header='internal')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
