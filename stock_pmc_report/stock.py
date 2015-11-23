# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Wang Liping
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
# from openerp.tools.translate import _
# from openerp.tools.safe_eval import safe_eval as eval
# import openerp.addons.decimal_precision as dp
# from openerp.tools.float_utils import float_round
import datetime


class stock_count(models.Model):
    _name = 'stock.count'

    _description = 'statistics stock inventory,On Hand ,Draft,Commit,Backorder,Available,On Order'

    product_id = fields.Many2one('product.product', 'Product')
    location_id = fields.Many2one('stock.location', 'Inventory Location')
    report_date = fields.Datetime('Report Date')
    on_hand_qty = fields.Float('ON hand')
    draft_qty = fields.Float('Draft')
    commit_qty = fields.Float('commit')
    backorder_qty = fields.Float('Backorder')
    available_qty = fields.Float('Available')
    on_order_qty = fields.Float('On Order')
    on_sale_qty = fields.Float('On Sale')

    _order = "product_id,location_id"

    @api.multi
    def compute_stock_report(self, product_ids=[], location_ids=[]):
        if not product_ids:
            product_ids = [x.id for x in self.env['product.product'].search([('active', '=', True)])]
        if not location_ids:
            location_ids = [x.id for x in self.env['stock.location'].search([('is_compute', '=', True)])]

        self.delete_stock_count_old_data(product_ids, location_ids)

        vals = self.prepare_stock_report_data(product_ids, location_ids)
        for val in vals:
            self.create(val)

    def delete_stock_count_old_data(self, product_ids=[], location_ids=[]):
        # if not product_ids and not location_ids :
        #     all_ids = self.search([("1","=","1")])
        #     all_ids.unlink()
        #     return
        count_ids = self.search([('product_id', 'in', product_ids), ('location_id', 'in', location_ids)])
        if count_ids:
            count_ids.unlink()
        # product_none_ids = self.search([('product_id','is',None)])
        # if product_none_ids:
        #     product_none_ids.unlink()

    def prepare_stock_report_data(self, product_ids=[], location_ids=[]):
        products = self.env['product.product'].browse(product_ids)
        draft_vals = self.prepare_draft_qty()
        vals = []
        # unimport_outgoing_qtys = {loc_id1:{product_id1: 20, product_id2:30},loc_id2:{product_id1: 30, product_id2:40}}

        for location in self.env['stock.location'].browse(location_ids):
            qtys = {}
            # products = products.with_context({'location': location.id})
            # qtys = products._product_available(location.id)
            qtys = self.pool.get('product.product')._product_available(self.env.cr,self.env.uid,product_ids,context={'location': location.id})
            # location_unimport_outgoing_qty = unimport_outgoing_qtys.get(location.id,{})

            for product in products:
                product_qtys = qtys.get(product.id, {})
                # product_unimport_outgoing_qty = location_unimport_outgoing_qty.get(product.id,0)
                outgoing_qty = product_qtys.get('outgoing_qty', 0)  # + product_unimport_outgoing_qty
                on_hand_qty = product_qtys.get('qty_available', 0)

                val_line = {
                    'product_id': product.id,
                    'location_id': location.id,
                    'report_date': datetime.datetime.today(),
                    'draft_qty': 0,
                    'on_hand_qty': on_hand_qty,
                    'commit_qty': self.prepare_commit(outgoing_qty, on_hand_qty),
                    'backorder_qty': self.prepare_backorder(outgoing_qty, on_hand_qty),
                    'available_qty': self.prepare_available(outgoing_qty, on_hand_qty),
                    'on_order_qty': product_qtys.get('incoming_qty', 0),
                    'on_sale_qty': outgoing_qty
                }

                if location.is_draft_location:
                    val_line.update({'draft_qty': draft_vals.get(product.id, 0)})
                vals.append(val_line)
        return vals

    def get_value_from_params(self):
        return

    # commit = (sale if on hand > sale else on hand)
    def prepare_commit(self, sale_qty, on_hand_qty):
        return min(sale_qty, on_hand_qty)

    # backorder = (sale - on hand if sale > on hand else 0)
    def prepare_backorder(self, sale_qty, on_hand_qty):
        if sale_qty >= on_hand_qty:
            return (sale_qty - on_hand_qty)
        return 0

    # available = (on hand - sale if on hand > sale else 0)
    def prepare_available(self, sale_qty, on_hand_qty):
        if on_hand_qty > sale_qty:
            return on_hand_qty - sale_qty
        return 0

    # draft = all unconfirmed order quantity
    def prepare_draft_qty(self):
        # get the draft qty from is_draft tag and state draft
        sale_orde_obj = self.env['sale.order']
        sale_order_draft_ids = [x.id for x in sale_orde_obj.search(
            [('is_draft', '=', 'True'), ('state', '=', 'draft')])]

        # get the draft product id ,product_uom_qty by read group
        order_line_obj = self.env['sale.order.line']
        count_res = order_line_obj.read_group([[
            'order_id', 'in', sale_order_draft_ids]], [
            'product_uom_qty', 'product_id'], ['product_id'])

        vals = {}
        for count in count_res:
            if count['product_id']:
                product_id = count['product_id'][0]
                draft_qty = count['product_uom_qty']
                vals[product_id] = draft_qty
        return vals


class stock_location(models.Model):
    _inherit = 'stock.location'

    is_draft_location = fields.Boolean(string='Is Draft Location', default=False)
    is_compute = fields.Boolean(string="In Multi Report", help="Whether to compute stock in multi report", default=False)
