# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class stock_inventory_report_wizard(models.TransientModel):
    '''
    Stock Inventory Statistic Wizard
    '''
    _name = 'stock.inventory.report.wizard'
    _descript = 'Multi-Level Stock Report'

    update_report = fields.Boolean(string='Update Report', default=True)
    update_leadtime = fields.Boolean(
        string='Update Lead Time',
        default=False)

    @api.multi
    def generate_stock_inventory_report(self):
        product_ids = []
        location_ids = []
        if self.update_report:
            self.env['stock.count'].compute_stock_report(
                product_ids, location_ids)
        if self.update_leadtime:
            products = self.env['product.product'].search([])
            for product in products:
                product.update_product_leadtime(product_qty=1,
                                                rule_id=None,
                                                realtime=False
                                                )
        action = self.go_to_stock_count_tree_view()
        return action

    @api.multi
    def go_to_stock_count_tree_view(self):
        mod_obj = self.env['ir.model.data']
        action_id = mod_obj.get_object_reference(
            'stock_pmc_report',
            'action_product_statistic_tree',
        )
        action_id = action_id and action_id[1]

        final_url = "/web#page=0&limit=&view_type=\
            list&model=stock.count&action=" + str(action_id)
        return {'type': 'ir.actions.act_url',
                'url': final_url, 'target': 'self'}
