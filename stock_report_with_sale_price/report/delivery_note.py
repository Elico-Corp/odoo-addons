# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


import time

from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
from openerp.osv import osv, orm
from openerp.addons.report_multi_printout_formats.tools import is_default_lang


class delivery_note(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        # Warning on internal picking if there is not sale order
        if context is None:
            context = {}
        picking_obj = pooler.get_pool(cr.dbname).get('stock.picking')
        if context.get('active_ids', False):
            for picking in picking_obj.browse(
                    cr, uid, context['active_ids'], context=context):
                if not picking.sale_id:
                    raise osv.except_osv(
                        _('Warning!'),
                        _('There is no related sale order to this'
                            ' delivery document. Please use picking'
                            ' slip instead.'))

        super(delivery_note, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total_qty': self._get_total_qty,
            'is_default_lang': is_default_lang,
            'cr': self.cr,
            'uid': self.uid,
            'self': self,
            'check_access_rights': self._check_access_rights
        })

    def _check_access_rights(self, sale_order, context=None):
        sale_obj = self.pool.get('sale.order')
        res = True
        try:
            sale_obj.check_access_rule(self.cr, self.uid, [sale_order.id], 'read')
        except (orm.except_orm, ValueError):
            res = False
        return res

    def _get_total_qty(self, so):
        qty = sum([x.product_uom_qty for x in so.order_line])
        return qty

report_sxw.report_sxw(
    'report.print.delivery.note.internal',
    'stock.picking',
    'addons/stock_report_with_sale_price/report/delivery_note.rml',
    parser=delivery_note, header="external")
report_sxw.report_sxw(
    'report.print.delivery.note.out',
    'stock.picking.out',
    'addons/stock_report_with_sale_price/report/delivery_note.rml',
    parser=delivery_note, header="external")


