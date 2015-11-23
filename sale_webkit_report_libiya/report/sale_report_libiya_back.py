import time
from openerp.report import report_sxw
from openerp.osv import osv
# from openerp import api, models

class sale_report_libiya(report_sxw.rml_parse):
    _name = 'report.sale_webkit_report_libiya.report_sale_order_libiya'

    def _curr_rec(self, curr_ids):
        res = self.pool.get('res.currency').browse(self.cr, self.uid, curr_ids)
        return res.name

    def _compute_currency(self,to_currency, from_currency, amt, context=None):
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        amount = currency_obj.compute(self.cr, self.uid, to_currency, from_currency, amt,context=context)
        return amount

    def _curr_group(self,order_line):
        ids = map(lambda x: x.id, order_line)
        t={}
        self.cr.execute("select p.purchase_currency_id,t.type from \
                        sale_order_line as l\
                        LEFT JOIN product_product as p ON (l.product_id=p.id) \
                        LEFT JOIN sale_order as s  ON (l.order_id=s.id)\
                        LEFT JOIN product_template as t ON (p.product_tmpl_id=t.id) where l.id IN %s \
                        GROUP BY p.purchase_currency_id,t.type", (tuple(ids),))
        t = self.cr.fetchall()
        return t

    def _curr_line(self,order_line):
        ids = map(lambda x: x.id, order_line)
        self.cr.execute("select l.id,l.name,p.purchase_currency_id,l.product_uom_qty,l.price_unit,l.discount,t.type from \
                        sale_order_line as l\
                        LEFT JOIN product_product as p ON (l.product_id=p.id)\
                        LEFT JOIN product_template as t ON (p.product_tmpl_id=t.id) \
                        LEFT JOIN sale_order as s  ON (l.order_id=s.id) where l.id IN %s \
                        GROUP BY l.product_uom_qty,l.price_unit,l.id,l.name,p.purchase_currency_id,l.discount,t.type", (tuple(ids),))
        t = self.cr.fetchall()
        return t

    def __init__(self, cr, uid, name, context):
        super(sale_report_libiya, self).__init__(
            cr, uid, name, context=context)
        report_obj = self.env['report']

        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'curr_line': self._curr_line,
            'curr_group': self._curr_group,
            'curr_rec': self._curr_rec,
            'compute_currency': self._compute_currency,
        })
    

class report_pos_details(osv.AbstractModel):
    _name = 'report.sale_webkit_report_libiya.report_sale_order_libiya'
    _inherit = 'report.abstract_report'
    _template = 'sale_webkit_report_libiya.report_sale_order_libiya'
    _wrapped_report_class = sale_report_libiya


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
