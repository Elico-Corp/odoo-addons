# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class landed_cost_position(orm.Model):
    _inherit = 'landed.cost.position'

    _columns = {
        'report_generated': fields.boolean(
            'Generated report', help='this field is just for recording if'
            'this lc has been generated to the reporting accordingly')
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        '''rewrite the copy_data method to avoid copy the field:
        report_generated'''
        default = default or {}
        default.update({'report_generated': False})
        return super(landed_cost_position, self).copy_data(
            cr, uid, id, default, context=context)


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _get_total_value(self, cr, uid, picking, context=None):
        '''get the total value of the picking'''
        # TODO: do the uom conversion.
        tot_value = 0.0
        move_obj = self.pool.get('stock.move')
        for move in picking.move_lines:
            tot_value += move_obj._get_total_value(
                cr, uid, move, context=context)
        return tot_value

    def _get_total_quantity(self, picking):
        '''get the total quantity of the picking'''
        # TOFIX: do the uom conversion
        tot_quantity = 0
        for l in picking.move_lines:
            tot_quantity += l.product_qty
        return tot_quantity

    def _get_total_volume(self, picking):
        '''get the total volume'''
        tot_volume = 0.0
        for l in picking.move_lines:
            tot_volume += l.line_volume
        return tot_volume

    def _prepare_lc_report_data(
            self, cr, uid, move, picking_lc, amount,
            amount_currency, context=None):
        '''prepare the data to generate a new record of lc report
        :param move: browse_record object of stock move Model
        :param picking_lc: browse_record object of lc model'''

        def _get_id(obj):
            return obj and obj.id or False

        def _get_purchase_id(lc, move):
            purchase_id = _get_id(lc.purchase_order_id)
            if not purchase_id:
                purchase_id = _get_id(move.purchase_line_id and
                                      move.purchase_line_id.order_id or False)
            return purchase_id
        # get the period
        period_obj = self.pool.get('account.period')
        period = period_obj.find(cr, uid, move.date, context=context)

        lc_obj = self.pool.get('landed.cost.position')
        move_obj = self.pool.get('stock.move')
        res = lc_obj.copy_data(cr, uid, picking_lc.id, context=context) or {}
        res.update({
            'product_id': picking_lc.product_id.id,
            'partner_id': picking_lc.partner_id.id,
            'period_id': period[0],
            'amount': amount,
            'amount_currency': amount_currency,
            'move_id': move.id,
            'company_id': _get_id(picking_lc.company_id),
            'distribution_type_id': _get_id(picking_lc.distribution_type_id),
            'picking_id': _get_id(picking_lc.picking_id),
            'picking_info_id': _get_id(picking_lc.picking_info_id),
            'purchase_order_id': _get_purchase_id(picking_lc, move),
            'purchase_order_info_id': _get_purchase_id(picking_lc, move),
            'purchase_order_line_id': _get_id(picking_lc.purchase_order_line_id or
                                              move.purchase_line_id),
            'total_value': move_obj._get_total_value(cr, uid, move, context=context),
            'total_quantity': move.product_qty,
        })
        # to check if the return value is ok
        return res

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        res = super(stock_picking, self).do_partial(
            cr, uid, ids, partial_datas, context=context)
        self.action_create_lc_report(cr, uid, ids, context=context)
        return res

    def action_create_lc_report(self, cr, uid, ids, context=None):
        '''create the lc reporting when the stock move is confirmed.'''
        # TOFIX: once the stock picking is transfered, we cannot moodify the
        #   LC any more. when we need to cancel the LC, we might need to
        #   cancel the LC report as well.

        # create the lc reporting records accordingly.
        lc_obj = self.pool.get('landed.cost.position')
        move_obj = self.pool.get('stock.move')
        lc_report_obj = self.pool.get('landed.costs.reporting')
        precision_obj = self.pool.get('decimal.precision')
        prec = precision_obj.precision_get(cr, uid, 'Account') + 5
        for picking in self.browse(cr, uid, ids, context=context):
            # get total value:
            tot_value = self._get_total_value(cr, uid, picking, context=context)
            # get total quantity:
            tot_quantity = self._get_total_quantity(picking)
            # get total volume:
            tot_volume = self._get_total_volume(picking)

            for picking_lc in picking.landed_cost_line_ids:
                # distribute the lc for the moves in this picking.
                if picking_lc.distribution_type_id.landed_cost_type == 'value'\
                        and not picking_lc.report_generated:
                    for move in picking.move_lines:
                        move_value = move_obj._get_total_value(
                            cr, uid, move, context=context)
                        amount = round(
                            picking_lc.amount * move_value / tot_value, prec)
                        amount_currency = round(
                            picking_lc.amount_currency * move_value / tot_value,
                            prec)
                        lc_data = self._prepare_lc_report_data(
                            cr, uid, move, picking_lc, amount,
                            amount_currency, context=context)
                        lc_report_obj.create(cr, uid, lc_data, context=context)
                elif picking_lc.distribution_type_id.landed_cost_type == 'volume'\
                        and not picking_lc.report_generated:
                    for move in picking.move_lines:
                        move_volume = move.line_volume
                        amount = round(
                            picking_lc.amount * move_volume / tot_volume,
                            prec)
                        amount_currency = round(
                            picking_lc.amount_currency * move_volume / tot_volume,
                            prec)
                        lc_data = self._prepare_lc_report_data(
                            cr, uid, move, picking_lc, amount,
                            amount_currency, context=context)
                        lc_report_obj.create(cr, uid, lc_data, context=context)
                elif picking_lc.distribution_type_id.landed_cost_type == 'per_unit'\
                        and not picking_lc.report_generated:
                    for move in picking.move_lines:
                        move_qty = move.product_qty
                        amount = round(
                            picking_lc.amount * move_qty / tot_quantity,
                            prec)
                        amount_currency = round(
                            picking_lc.amount_currency * move_qty / tot_quantity,
                            prec)
                        lc_data = self._prepare_lc_report_data(
                            cr, uid, move, picking_lc, amount,
                            amount_currency, context=context)
                        lc_report_obj.create(cr, uid, lc_data, context=context)
                # write back the flag field
                picking_lc.write({'report_generated': True}, context=context)

            # duplicate the lc from stock move
            for move in picking.move_lines:
                for lc in move.landed_cost_line_ids:
                    if lc.report_generated:
                        continue
                    lc_data = self._prepare_lc_report_data(
                        cr, uid, move, lc, lc.amount,
                        lc.amount_currency, context=context)
                    lc_report_obj.create(cr, uid, lc_data, context=context)
                    # write back the flag field
                    lc.write({'report_generated': True}, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.action_create_lc_report(cr, uid, ids, context=context)
        res = super(stock_picking, self).action_done(
            cr, uid, ids, context=context)
        return res


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _get_total_value(self, cr, uid, move, context=None):
        '''get total value of stock move'''
        # recalculate the unit price for the move when it is partial receive.
        # this is only for IS from purchase order.
        # TODO do the uom conversion
        # we convert the value to company currency.
        context = context or {}
        # use the date when the move is done to get the currency.
        context.update({'date': move.date})
        cur_obj = self.pool.get('res.currency')
        if move.purchase_line_id:
            from_currency = move.purchase_line_id.order_id.currency_id
            from_currency_id = from_currency and from_currency.id or False
            to_currency = move.company_id.currency_id
            to_currency_id = to_currency and to_currency.id or False
            from_amount = move.purchase_line_id.price_subtotal
            to_amount = cur_obj.compute(
                cr, uid, from_currency_id, to_currency_id,
                from_amount, round=True, context=context)
            return to_amount
        else:
            # get right standard price
            price_history_obj = self.pool.get('product.price.history')
            standard_price = price_history_obj._get_historic_price(
                cr, uid, [move.product_id.id], move.company_id.id,
                datetime=move.date, field_names=['standard_price'],
                context=context)
            return standard_price.get('standard_price', 0) * move.product_qty
