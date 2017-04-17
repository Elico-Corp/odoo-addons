import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp.tools.translate import _


class sale_report_libiya(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_report_libiya, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'curr_line': self.curr_line,
            'curr_group': self.curr_group,
            'curr_rec': self.curr_rec,
            'compute_currency': self.compute_currency,
            'curr_group_value': self.curr_group_value,
            'order_discount': self._order_discount,

        })

    def curr_rec(self, curr_ids):
        res = self.pool.get('res.currency').browse(self.cr, self.uid, curr_ids)
        return res.name

    def compute_currency(self, to_currency, from_currency, amt, context=None):
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        amount = currency_obj.compute(self.cr, self.uid, to_currency, from_currency, amt,context=context)
        return amount

    def curr_group(self, order_line):
        ids = map(lambda x: x.id, order_line)
        t = {}
        self.cr.execute("select p.purchase_currency_id,t.type from \
                        sale_order_line as l\
                        LEFT JOIN product_product as p ON (l.product_id=p.id) \
                        LEFT JOIN sale_order as s  ON (l.order_id=s.id)\
                        LEFT JOIN product_template as t ON (p.product_tmpl_id=t.id) where l.id IN %s \
                        GROUP BY p.purchase_currency_id, t.type", (tuple(ids),))
        t = self.cr.fetchall()
        return t

    def curr_group_value(self, order):
        """
            group[0]: purchase_currency_id
            group[1]: product type
        """
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        sol_obj = self.pool.get('sale.order.line')

        res = {}
        order_line = order.order_line
        company_currency_id = order.company_id.currency_id.id
        order_curreny_id = order.currency_id.id

        for line in order_line:
            if line.product_id.type == 'service':
                continue
            pur_cur_id = line.pur_currency_id.id # xie
            if not pur_cur_id:
                pur_cur_id = line.product_id and line.product_id.purchase_currency_id.id or company_currency_id
            if pur_cur_id != order_curreny_id:
            # line purchase currency is not order currency
                if not pur_cur_id in res:
                    res[pur_cur_id] = {}
                    res[pur_cur_id].update({
                        # 'purchase_currency_id': line.product_id.purchase_currency_id,
                        'purchase_currency_id': line.pur_currency_id or line.product_id.purchase_currency_id,
                        'price_subtotal': 0,
                        'discount': 0,
                        'price_total': 0,
                        'lines': [],
                    })
                discount = self.compute_currency(
                        order_curreny_id, pur_cur_id,
                        line.price_unit * line.product_uom_qty - line.price_subtotal)
                price_subtotal = self.compute_currency(
                        order_curreny_id, pur_cur_id,
                        line.price_subtotal)
                price_total = self.compute_currency(
                        order_curreny_id, pur_cur_id,
                        line.price_unit * line.product_uom_qty)

                pur_price_unit = line.pur_price_unit
                if not pur_price_unit:
                    pur_price_unit = self.compute_currency(
                        order_curreny_id, pur_cur_id, line.price_unit)
                pur_price_subtotal = line.pur_price_subtotal
                if not pur_price_subtotal:
                    pur_price_subtotal = price_total

                line_value = {
                    'id': line.id,
                    'product_name': line.product_id.name,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    # 'price_unit': self.compute_currency(
                    #     order_curreny_id, pur_cur_id, line.price_unit),
                    # 'price_total': price_total,
                    # xie
                    'price_unit': pur_price_unit,
                    'price_total': pur_price_subtotal,
                    'discount': discount,
                    'discount_per': line.discount,
                    'price_subtotal': price_subtotal,
                }

                res[pur_cur_id]['lines'].append(line_value)
                res[pur_cur_id].update({
                    'discount': res[pur_cur_id]['discount'] + discount,
                    'price_total': res[pur_cur_id]['price_total'] + price_total,
                    'price_subtotal': res[pur_cur_id]['price_subtotal'] + price_subtotal,
                    })
                # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                # taxes = tax_obj.compute_all(
                #     self.cr, self.uid, line.tax_id,
                #     price, line.product_uom_qty,
                #     line.product_id, line.order_id.partner_id)
                # print taxes
            # res[line.id].update({
            #     'subtotal': line.price_subtotal,
            #     'disc': tax['amount_all'],
            #     'total': tax.amount_all,
            #     'product_uom_qty': line.product_uom_qty,
            #     })
            # subtotal += ine.price_subtotal
            # disc = line.price_reduce
            # total = line.amount_all
            else:
                # line purchase currency is order currency
                if not order_curreny_id in res:
                    res[order_curreny_id] = {}
                    res[order_curreny_id].update({
                        'purchase_currency_id': order.currency_id,
                        'price_subtotal': 0,
                        'discount': 0,
                        'price_total': 0,
                        'lines': []
                    })
                discount = line.price_unit * line.product_uom_qty - line.price_subtotal
                price_subtotal = line.price_subtotal
                price_total = line.price_unit * line.product_uom_qty
                line_value = {
                    'id': line.id,
                    'product_name': line.product_id.name,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'discount': discount,
                    'discount_per': line.discount,
                    'price_subtotal': price_subtotal,
                    'price_total': price_total
                }

                res[pur_cur_id]['lines'].append(line_value)
                res[pur_cur_id].update({
                    'discount': res[pur_cur_id]['discount'] + discount,
                    'price_total': res[pur_cur_id]['price_total'] + price_total,
                    'price_subtotal': res[pur_cur_id]['price_subtotal'] + price_subtotal,
                    })
        return res

    def _order_discount(self, order):
        res = {}
        service = []
        discount = 0
        price_subtotal = 0
        price_total = 0

        for line in order.order_line:
            discount += line.price_unit * line.product_uom_qty - line.price_subtotal
            price_subtotal += line.price_subtotal
            price_total += line.price_unit * line.product_uom_qty
            if line.product_id.type == 'service':
                service.append((line.product_id.name, line.price_unit))

        res.update({
            'discount': discount,
            'price_subtotal': price_subtotal,
            'price_total': price_total,
            'other': [],
            })

        if service:
            res.update({'other': service})
        # res = [price_total, discount, price_subtotal]
        return res

    def curr_line(self, order_line):
        ids = map(lambda x: x.id, order_line)
        self.cr.execute("select l.id,l.name,p.purchase_currency_id,l.product_uom_qty,l.price_unit,l.discount,t.type from \
                        sale_order_line as l\
                        LEFT JOIN product_product as p ON (l.product_id=p.id)\
                        LEFT JOIN product_template as t ON (p.product_tmpl_id=t.id) \
                        LEFT JOIN sale_order as s  ON (l.order_id=s.id) where l.id IN %s \
                        GROUP BY l.product_uom_qty,l.price_unit,l.id,l.name,p.purchase_currency_id,l.discount,t.type", (tuple(ids),))
        t = self.cr.fetchall()
        return t


class report_pos_details(osv.AbstractModel):
    _name = 'report.sale_webkit_report_libiya.report_sale_order_libiya'
    _inherit = 'report.abstract_report'
    _template = 'sale_webkit_report_libiya.report_sale_order_libiya'
    _wrapped_report_class = sale_report_libiya


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
