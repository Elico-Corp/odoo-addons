# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import datetime


class ProductCostBatch(models.Model):
    _name = 'product.cost.batch'

    name = fields.Char(string='Name', required=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    date_start = fields.Date(
        string='Date From',
        required=True,
        readonly=True,
        default=datetime.date(
            datetime.date.today().year,
            datetime.date.today().month - 1,
            1
        ),
        states={'draft': [('readonly', False)]}
    ),
    date_to = fields.Date(string='Date End', required=True,
                          readonly=True,
                          default=(
                              datetime.date(
                                  datetime.date.today().year,
                                  datetime.date.today().month, 1
                              ) - datetime.timedelta(1)),
                          states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('close', 'Close'),
                              ], string='Status', select=True,
                             readonly=True, copy=False, default='draft')
    cost_ids = fields.One2many(
        comodel_name='product.cost',
        inverse_name='cost_batch_id',
        string='Cost List',
        readonly=True, states={'draft': [('readonly', False)]})
    categ_id = fields.Many2many(
        comodel_name='product.category',
        string='Internal Category',
        required=True, change_default=True,
        domain="[('type','=','normal')]",
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Select category for the current product"
    )

    @api.multi
    def generate_product_cost_by_mrp(self):
        for batch in self:
            product_cost = batch.env['product.cost']
            manufacture = batch.env['mrp.production']
            cost_ids = batch.cost_ids
            if cost_ids:
                cost_ids.unlink()
            categ_ids = []
            for categ_id in batch.categ_id:
                categ_ids.append(categ_id.id)
                categ_ids.extend(categ_id.child_id.ids)
            domain = [('date_start', '<', batch.date_to),
                      ('date_start', '>', batch.date_start),
                      ('state', 'in', ('in_production', 'done')),
                      ('product_id.product_tmpl_id.categ_id.id',
                       'in', categ_ids)]
            mo_ids = manufacture.search(domain)
            for mrp in mo_ids:
                customer_id = False
                sale_income = 0
                finished_product_number = 0
                if mrp.sale_name:
                    sale_obj = batch.env['sale.order'].search(
                        [('name', '=', mrp.sale_name)])
                    customer_id = sale_obj.partner_id.id
                    sale_income = sale_obj.amount_total
                for finished_product in mrp.move_created_ids2:
                    if finished_product.product_qty:
                        finished_product_number +=\
                            finished_product.product_qty
                res = {
                    'cost_batch_id': batch.id,
                    'mo_id': mrp.id,
                    'customer_id': customer_id,
                    'product_name': mrp.product_id.id,
                    'finished_product_number': finished_product_number,
                    'sale_income': sale_income,
                }
                product_cost.create(res)

    @api.multi
    def draft_batch(self):
        return self.write({'state': 'draft'})

    @api.multi
    def close_batch(self):
        return self.write({'state': 'close'})

    @api.multi
    def product_cost_report(self):
        '''
        general description.

        @return:
        '''
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.product.cost.batch.report.xls',
            'report_type': 'xls',
            'datas': {},
        }


class ProductCost(models.Model):
    _name = 'product.cost'

    cost_batch_id = fields.Many2one(
        comodel_name='product.cost.batch',
        string='Cost Batch',
        ondelete='cascade')
    mo_id = fields.Many2one(
        comodel_name='mrp.production', string='Manufacture', required=True)
    customer_id = fields.Many2one(
        comodel_name='res.partner', string='Customer')
    product_name = fields.Many2one(
        comodel_name='product.product', string='Product Name',
        related='mo_id.product_id')
    product_code = fields.Char(string='Product Code',
                               related='product_name.default_code')
    uom = fields.Many2one(
        comodel_name='product.uom',
        related='product_name.uom_id',
        string='Uom')
    finished_product_number = fields.Float(string='Finished Product Number')
    sale_income = fields.Float(string='Sale Income')
    material_cost = fields.Float(string='Material Cost')
    resource_cost = fields.Float(string='Resource Cost')
    manufacture_cost = fields.Float(string='Manufacture Cost')
    total = fields.Float(string='Total', store=True,
                         readonly=True, compute='_compute_cost')
    sale_profit = fields.Float(string='Sale Profit',
                               store=True, readonly=True,
                               compute='_compute_cost')
    sale_profit_percent = fields.Float(string='Sale Profit Percent',
                                       store=True, readonly=True,
                                       compute='_compute_cost')
    unit_material_cost = fields.Float(string='Unit Material Cost',
                                      store=True, readonly=True,
                                      compute='_compute_cost')
    unit_resource_cost = fields.Float(string='Unit Resource Cost',
                                      store=True, readonly=True,
                                      compute='_compute_cost')
    unit_manufacture_cost = fields.Float(string='Unit Manufacture Cost',
                                         store=True, readonly=True,
                                         compute='_compute_cost')
    unit_cost = fields.Float(string='Unit Cost', store=True, readonly=True,
                             compute='_compute_cost')

    _sql_constraints = [
        ('mo_uniq', 'unique(mo_id)',
            'A product cost with the same manufacture already exists !'),
    ]

    @api.multi
    @api.depends('finished_product_number', 'sale_income',
                 'material_cost', 'resource_cost', 'manufacture_cost')
    def _compute_cost(self):
        for batch in self:
            batch.total = batch.material_cost + batch.resource_cost +\
                          batch.manufacture_cost
            if batch.total:
                batch.sale_profit = batch.sale_income - batch.total
                batch.sale_profit_percent =\
                    (batch.sale_profit / batch.total) * 100
            if batch.finished_product_number:
                batch.unit_material_cost = \
                    batch.material_cost / batch.finished_product_number
                batch.unit_resource_cost = \
                    batch.resource_cost / batch.finished_product_number
                batch.unit_manufacture_cost = \
                    batch.manufacture_cost / batch.finished_product_number
                batch.unit_cost = batch.total / batch.finished_product_number
