# -*- coding: utf-8 -*-
# © 2004-2010 Tiny SPRL (http://tiny.be)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import time
from openerp.report import report_sxw


class picking(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal': self.get_qtytotal,
            'get_amounttotal': self.get_amounttotal,
            'get_product_desc': self.get_product_desc,
            'get_product_desc_en': self.get_product_desc_en,
            'get_product_unit': self.get_product_unit,
            'get_product_price': self.get_product_price,
            'get_product_total': self.get_product_total,
            'get_location_name': self.get_location_name,
            'get_location_dest_name': self.get_location_dest_name,
        })

    def get_product_desc(self, product_id):
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
    # def get_product_desc(self, move_line):
    #     desc = move_line.product_id.name_sort_cn
    #     if move_line.product_id.default_code:
    #         desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
    #     return desc

    def get_product_desc_en(self, move_line):
        desc = move_line.product_id.name or ''
        return desc

    # def get_product_unit(self, move_line):
    #     desc = move_line.product_id.joomla_unit
    #     if move_line.product_id.joomla_unit_cn:
    #         desc = desc + ' / ' + move_line.product_id.joomla_unit_cn
    #     return desc
    def get_product_unit(self, move_line):
        desc = move_line.product_uom.name or ''
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

    def get_product_price(self, move_line):
        price = 0.0
        if move_line.purchase_line_id:
            price = move_line.po_price
        return price

    def get_product_total(self, move_line):
        total = 0.0
        if move_line.purchase_line_id:
            total = move_line.product_qty * move_line.po_price
        return total

    def get_qtytotal(self, move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total += move.product_qty
        return {'quantity': total, 'uom': uom}

    def get_amounttotal(self, move_lines):
        total = 0.0
        for move in move_lines:
            if move.purchase_line_id:
                total += move.product_qty * move.po_price
        return total

    def get_location_name(self, move_lines):
        desc = move_lines.location_id.name or ''
        trans_obj = self.pool.get('ir.translation')
        trans_ids = trans_obj.search(
            self.cr, self.uid,
            [('name', '=', 'stock.location,name'),
             ('res_id', '=', move_lines.location_id.id)])
        if trans_ids and trans_ids[0]:
            desc = desc + ' / ' + trans_obj.read(self.cr, self.uid, trans_ids,
                                                 ['value'])[0]['value']
        return desc

    def get_location_dest_name(self, move_lines):
        desc = move_lines.location_dest_id.name or ''
        trans_obj = self.pool.get('ir.translation')
        trans_ids = trans_obj.search(
            self.cr, self.uid,
            [('name', '=', 'stock.location,name'),
             ('res_id', '=', move_lines.location_dest_id.id)])
        if trans_ids and trans_ids[0]:
            desc = desc + ' / ' + trans_obj.read(self.cr, self.uid, trans_ids,
                                                 ['value'])[0]['value']
        return desc


#report_sxw.report_sxw('report.stock.picking.int.list.fc', 'stock.picking', 'addons/fc_reports/report/fc_picking_int.rml', parser=picking)
report_sxw.report_sxw(
    'report.stock.picking.in.list.elico1', 'stock.picking',
    'addons/l10n_cn_report_stock/report/elico_picking_in.rml', parser=picking)
#report_sxw.report_sxw('report.stock.picking.in.price.list.fc', 'stock.picking', 'addons/fc_reports/report/fc_picking_in_price.rml', parser=picking)
report_sxw.report_sxw(
    'report.stock.picking.out.list.elico1', 'stock.picking',
    'addons/l10n_cn_report_stock/report/elico_picking_out.rml', parser=picking)
#report_sxw.report_sxw('report.stock.picking.in.return.list.fc', 'stock.picking', 'addons/fc_reports/report/fc_picking_in_return.rml', parser=picking)
#report_sxw.report_sxw('report.stock.picking.out.return.list.fc', 'stock.picking', 'addons/fc_reports/report/fc_picking_out_return.rml', parser=picking)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
