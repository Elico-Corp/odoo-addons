# -*- coding: utf-8 -*-
# © 2004-2010 Tiny SPRL (http://tiny.be)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import time
from openerp.report import report_sxw
from openerp import pooler
from itertools import groupby


class sale_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update(
            {
                'time': time,
                'get_line_tax': self._get_line_tax,
                'get_tax': self._get_tax,
                'get_product_code': self._get_product_code,
                'multiply': self._multiply,
                'get_product_desc': self.get_product_desc,
                'get_product_desc_en': self.get_product_desc_en,
                'get_product_unit': self.get_product_unit,
            })

    def _get_line_tax(self, line_obj):
        self.cr.execute(
            "SELECT tax_id FROM purchase_order_taxe WHERE order_line_id=%s",
            (line_obj.id))
        res = self.cr.fetchall() or None
        if not res:
            return ""
        if isinstance(res, list):
            tax_ids = [t[0] for t in res]
        else:
            tax_ids = res[0]
        res = [tax.name for tax in pooler.get_pool(self.cr.dbname).get(
            'account.tax').browse(self.cr, self.uid, tax_ids)]
        return ",\n ".join(res)

    def _get_tax(self, order_obj):
        res = []
        real_lines = []
        for line in order_obj.order_line:
            for tax in line.taxes_id:
                real_lines.append({'line': line, 'tax': tax})
        for tax, val_iter in groupby(real_lines, lambda x: x['tax']):
                base = sum(val['line'].price_subtotal for val in val_iter)
                res.append({'tax': tax.amount,
                            'code': tax.name,
                            'base': base,
                            'amount': base * tax.amount})
        res.sort(lambda x, y: int(x['tax'] - y['tax'] * 1000000))
        return res

    def _get_product_code(self, product_id, partner_id):
        product_obj = pooler.get_pool(self.cr.dbname).get('product.product')
        return product_obj._product_code(
            self.cr, self.uid, [product_id], name=None, arg=None,
            context={'partner_id': partner_id})[product_id]

    def _multiply(self, one, two):
        return one * two

    # def get_product_desc(self, move_line):
    #     desc = move_line.name or ''
    #     if move_line.product_id.default_code:
    #         desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
    #     return desc
    def get_product_desc(self, product_id):
        print "\n\nproduct_id %s \n\n" % product_id
        # get desc cn for name, default_cdde, uom
        trans_obj = self.pool.get('ir.translation')
        #name
        trans_ids = trans_obj.search(
            self.cr, self.uid,
            [('name', '=', 'product.template,name'),
             ('src', '=', product_id.name)])
        if trans_ids and trans_ids[0]:
            desc = trans_obj.read(self.cr, self.uid, trans_ids,
                                  ['value'])[0]['value']
        else:
            desc = u'无'
        # if product_id.default_code:
        #     desc = '[' + product_id.default_code + ']' + ' ' + desc
        return desc

    def get_product_desc_en(self, move_line):
        desc = move_line.product_id.name or ''
        return desc

    def get_product_unit(self, move_line):
        desc = move_line.product_uom.name or ''
        print "\n\ndesc %s\n\n" % desc
        trans_obj = self.pool.get('ir.translation')
        trans_ids = trans_obj.search(
            self.cr, self.uid,
            [('name', '=', 'product.uom,name'),
             ('res_id', '=', move_line.product_uom.id)])
        # if move_line.product_id.joomla_unit_cn:
        #     desc = desc + ' / ' + move_line.product_id.joomla_unit_cn
        if trans_ids and trans_ids[0]:
            desc = desc + ' / ' + trans_obj.read(self.cr, self.uid, trans_ids,
                                                 ['value'])[0]['value']
        return desc


report_sxw.report_sxw(
    'report.sale.order.elico1', 'sale.order',
    'addons/l10n_cn_report_sale/report/sale_order_quotation.rml',
    parser=sale_order)
#report_sxw.report_sxw(
#    'report.purchase.order.requisition.fc', 'purchase.order',
#    'addons/fc_reports/report/fc_po_requisition.rml', parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
