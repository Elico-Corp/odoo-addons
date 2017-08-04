# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields, osv
import openerp.addons.decimal_precision as dp


class landed_costs_shipment(orm.Model):
    _name = 'landed.costs.shipment'

    _columns = {
        'name': fields.char('Name', size=60, required=True, readonly=True),
        'port_of_departure': fields.char('Port of departure', size=256),
        'departure_date': fields.date('Departure date', size=256),
        'port_of_arrival': fields.char('Port of arrival', size=256),
        'arrival_date': fields.date('Arrival date'),
        'vessel': fields.char('Vessel', size=256),
        'company_id': fields.many2one('res.company', 'Company', ondelete="set null"),
        'po_ids': fields.one2many('purchase.order', 'shipment_id', 'Purchase Orders'),
        'lc_template_ids': fields.one2many(
            'landed.cost.position.template', 'shipment_id', 'Landed Cost Lines'),
        'state': fields.selection(
            [('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')],
            'Status', required=True, readonly=True,)
    }

    _defaults = {
        'name': '/',
        'state': 'draft'
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Order Reference must be unique per Company!'),
    ]

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'landed.costs.shipment')
        return super(landed_costs_shipment, self).create(
            cr, uid, vals, context=context)

    def _generate_landed_cost_for_purchase(self, cr, uid, purchase, amount, template, context=None):
        prod_obj = self.pool.get('product.product')
        lc_obj = self.pool.get('landed.cost.position')
        currency_id = template.currency_id and template.currency_id.id or False
        purchase_currency_id = purchase.pricelist_id and purchase.pricelist_id.currency_id and \
            purchase.pricelist_id.currency_id.id or False
        vals = {
            'shipment_id': template.shipment_id.id,
            'template_id': template.id,
            'product_id': template.product_id.id,
            'partner_id': template.partner_id.id,
            'generate_invoice': template.generate_invoice,
            'distribution_type_id': template.distribution_type_id.id,
            'amount_currency': amount,
            'amount': amount,
            'currency_id': currency_id,
            'purchase_order_id': purchase.id,
            'po_currency_id': purchase_currency_id,
        }
        # get the fiscal position and right fiscal account
        fiscal_position = purchase.fiscal_position or False
        prod = prod_obj.browse(cr, uid, template.product_id, context=context)
        account_id = prod_obj._choose_exp_account_from(
            cr, uid, prod, fiscal_position=fiscal_position, context=context)
        vals['account_id'] = account_id
        # compute the amount of between different currencies
        if currency_id != purchase_currency_id:
            cur_obj = self.pool.get('res.currency')
            ctx = context.copy()
            ctx['date'] = purchase.date_order or False
            amount_computed = cur_obj.compute(
                cr, uid,
                currency_id,
                purchase_currency_id,
                amount,
                context=ctx)
            vals['amount'] = amount_computed
        lc_id = lc_obj.create(cr, uid, vals, context=context)
        return lc_id

    def button_confirm(self, cr, uid, ids, context=None):
        for shipment in self.browse(cr, uid, ids, context=context):
            volume_total = 0.0
            amount_total = 0.0
            quantity_total = 0.0
            amount = 0
            if (not shipment.lc_template_ids) or (not shipment.po_ids):
                raise osv.except_osv(
                    ('Warning'),
                    ('You should add more than 1 landed cost template or purchase order.'))
            for purchase in shipment.po_ids:
                quantity_total += purchase.quantity_total
                volume_total += purchase.volume_total
                amount_total += purchase.amount_untaxed
            for template in shipment.lc_template_ids:
                for purchase in shipment.po_ids:
                    cost_type = template.distribution_type_id.landed_cost_type
                    if cost_type == 'volume':
                        amount = (purchase.volume_total * template.amount) / volume_total
                    elif cost_type == 'value':
                        amount = (purchase.amount_total * template.amount) / amount_total
                    elif cost_type == 'per_unit':
                        amount = (purchase.quantity_total * template.amount) / quantity_total
                    else:
                        amount = (purchase.amount_total * template.amount) / amount_total
                    self._generate_landed_cost_for_purchase(
                        cr, uid, purchase, amount, template, context=context)
            shipment.write({'state': 'done'})
            return True
        return False

    def button_clear_purchase(self, cr, uid, ids, context=None):
        for shipment in self.browse(cr, uid, ids, context=context):
            for po in shipment.po_ids:
                po.write({'shipment_id': False}, context=context)
        return True


class landed_cost_position_template(orm.Model):
    _name = 'landed.cost.position.template'
    # _inherit = 'landed.cost.position'

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Landed Cost Name',
            required=True,
            domain=[('landed_cost_type', '!=', False)]),
        'account_id': fields.many2one(
            'account.account',
            'Fiscal Account',
            required=True,),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            help="The supplier of this cost component.",
            required=True),
        'distribution_type_id': fields.many2one(
            'landed.cost.distribution.type',
            'Distribution Type',
            required=True,
            domain=[('apply_on', '=', 'order')],
            help="Defines if the amount is to be calculated for each quantity "
                 "or an absolute value"),
        'generate_invoice': fields.boolean(
            'Generate Invoice',
            help="If ticked, this will generate a draft invoice at the "
                 "PO confirmation for this landed cost position from the "
                 "related partner. If not, no invoice will be generated, "
                 "but the cost will be included for the average price "
                 "computation."),
        'currency_id': fields.many2one(
            'res.currency', 'Currency'),
        'amount': fields.float(
            'Amount',
            required=True,
            digits_compute=dp.get_precision('Purchase Price'),
            help="Landed cost expressed in PO currency used "
                 "to fullfil landed cost."),

        'shipment_id': fields.many2one('landed.costs.shipment', 'Shipment'),
        'lc_ids': fields.one2many('landed.cost.position', 'template_id', 'Landed Costs')
    }

    def onchange_product_id(self, cr, uid, ids, product_id,
                            purchase_order_id=False, context=None):
        """ Give the default value for distribution_type_id, Ficial account, partner_id

         """
        res = {}
        landed_cost_type = False

        apply_on = 'order'
        if not product_id:
            return res
        prod_obj = self.pool.get('product.product')
        dist_type_obj = self.pool.get('landed.cost.distribution.type')
        prod = prod_obj.browse(cr, uid, [product_id], context=context)[0]
        account_id = prod_obj._choose_exp_account_from(
            cr, uid, prod, fiscal_position=False, context=context)
        if prod.landed_cost_type in ('per_unit', 'value', 'volume'):
            landed_cost_type = dist_type_obj.search(
                cr, uid,
                [('apply_on', '=', apply_on),
                 ('landed_cost_type', '=', prod.landed_cost_type)],
                context=context)[0]
        value = {
            'distribution_type_id': landed_cost_type,
            'account_id': account_id,
            'partner_id': prod.seller_id and prod.seller_id.id or False
        }
        res = {'value': value}
        return res
