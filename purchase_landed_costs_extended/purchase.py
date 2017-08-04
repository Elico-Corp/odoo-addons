# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class landed_cost_position(orm.Model):
    _inherit = 'landed.cost.position'

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if not partner_id:
            return {}
        partner = self.pool.get('res.partner').browse(
            cr, uid, partner_id, context=context)
        pricelist = partner.property_product_pricelist_purchase
        currency_id = pricelist.currency_id
        return {'value': {'currency_id': currency_id and currency_id.id or False}}

    def onchange_amount_currency(self, cr, uid, ids,
                                 amount_currency, currency_id,
                                 date_po, context=None):
        assert len(ids) < 2
        parent_currency_id = None
        if ids:
            landed_cost = self.browse(cr, uid, ids[0], context=context)
            parent_currency_id = landed_cost.po_currency_id.id
        else:
            parent_currency_id = self._default_currency(
                cr, uid, context=context)
        if not parent_currency_id or not amount_currency or not currency_id:
            return {}
        cur_obj = self.pool.get('res.currency')
        amount = amount_currency
        if currency_id != parent_currency_id:
            ctx = context.copy()
            ctx['date'] = date_po or False
            amount = cur_obj.compute(cr, uid,
                                     currency_id,
                                     parent_currency_id,
                                     amount,
                                     context=ctx)
        return {'value': {'amount': amount}}

    def _default_currency(self, cr, uid, context=None):
        context = context or {}
        pricelist_id = context.get('pricelist_id', [])
        pricelist = self.pool.get('product.pricelist').read(
            cr, uid, pricelist_id, ['currency_id'])
        parent_currency_id = None
        if pricelist:
            parent_currency_id = pricelist['currency_id'][0]
        return parent_currency_id

    _columns = {
        'amount_currency': fields.float(
            'Currency Amount',
            digits_compute=dp.get_precision('Purchase Price'),
            help="Landed cost expressed in Landed Cost line currency"),
        'currency_id': fields.many2one(
            'res.currency', 'Currency'),
        'po_pricelist_id': fields.related(
            'purchase_order_id', 'pricelist_id',
            type='many2one',
            relation='product.pricelist',
            string='PO Pricelist',
            store=True,
            readonly=True,
            help="PO pricelist"),
        'po_currency_id': fields.related(
            'po_pricelist_id', 'currency_id',
            type='many2one',
            relation='res.currency',
            string='PO Currency',
            store=True,
            readonly=True,
            help="PO Currency"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'active': fields.boolean('Active'),
        # once the template is deleted, this record should be deleted as well
        'template_id': fields.many2one(
            'landed.cost.position.template', 'Landed costs template',
            ondelete='restrict'),
        'shipment_id': fields.many2one(
            'landed.costs.shipment', 'Landed Costs Shipment')
    }

    _defaults = {
        'currency_id': _default_currency,
        'active': True
    }

    def open_invoice(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        lcp = self.browse(cr, uid, ids[0], context=context)
        if not lcp.invoice_id:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Form heading',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.invoice',
            'nodestroy': True,
            'res_id': lcp.invoice_id.id,
            'context': context
        }

    def onchange_product_id(self, cr, uid, ids, product_id,
                            purchase_order_id=False, context=None):
        """ Give the default value for the distribution type depending
        on the setting of the product and the use case: line or order
        position.

        rewrite this method from parent

         """
        res = {}
        fiscal_position = False
        landed_cost_type = False
        # order or line depending on which view we are
        if purchase_order_id:
            apply_on = 'order'
            po_obj = self.pool.get('purchase.order')
            po = po_obj.browse(cr, uid, purchase_order_id, context=context)
            fiscal_position = po.fiscal_position or False
        else:
            apply_on = 'line'
        if not product_id:
            return res
        prod_obj = self.pool.get('product.product')
        dist_type_obj = self.pool.get('landed.cost.distribution.type')
        prod = prod_obj.browse(cr, uid, [product_id], context=context)[0]
        account_id = prod_obj._choose_exp_account_from(
            cr, uid, prod, fiscal_position=fiscal_position, context=context)
        # here we add a new distribution type
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

    def _get_total_amount(self, cr, uid, landed_cost, context=None):
        """ We should have a field that is the computed value (total
        costs that land) e.g. if it's related to a line and per_unit =>
        I want for the reporting the total line landed cost and multiply
        the quantity by given amount.

        :param browse_record landed_cost: Landed cost position browse record
        :return total value of this landed cost position

        """
        # TO be checked
        vals_po_currency = 0.0
        if (landed_cost.purchase_order_line_id and
                landed_cost.distribution_type_id.landed_cost_type == 'per_unit'):
            vals_po_currency = (landed_cost.amount *
                                landed_cost.purchase_order_line_id.product_qty)
        elif (landed_cost.purchase_order_line_id and
                landed_cost.distribution_type_id.landed_cost_type == 'volume'):
            vals_po_currency = (landed_cost.amount *
                                landed_cost.purchase_order_line_id.line_volume)
        else:
            vals_po_currency = landed_cost.amount
        return vals_po_currency


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _generate_invoice_from_landed_cost(self, cr, uid, landed_cost,
                                           context=None):
        if landed_cost.invoice_id:
            return landed_cost.invoice_id.id
        inv_id = super(
            purchase_order, self
        )._generate_invoice_from_landed_cost(
            cr, uid, landed_cost, context=context)
        landed_cost.write({'invoice_id': inv_id}, context=context)
        return inv_id

    def _prepare_landed_cost_inv_line(self, cr, uid, account_id, inv_id,
                                      landed_cost, context=None):
        res = super(purchase_order, self)._prepare_landed_cost_inv_line(
            cr, uid, account_id, inv_id, landed_cost, context=context)
        res['price_unit'] = landed_cost.amount_currency
        return res

    def _prepare_landed_cost_inv(self, cr, uid, landed_cost, context=None):
        res = super(purchase_order, self)._prepare_landed_cost_inv(
            cr, uid, landed_cost, context=context)
        res['currency_id'] = landed_cost.currency_id.id
        return res

    def wkf_approve_order(self, cr, uid, ids, context=None):
        """ On PO approval, generate all invoices for all landed cost position.

        Remember that only landed cost position with the checkbox
        generate_invoice ticked are generated.

        """
        lcp_pool = self.pool.get('landed.cost.position')
        line_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            for po_line in order.order_line:
                for line_cost in po_line.landed_cost_line_ids:
                    if not line_cost.generate_invoice or line_cost.invoice_id:
                        line_ids = line_cost.id
        lcp_pool.write(cr, uid, line_ids, {'active': False})

        res = super(purchase_order, self).wkf_approve_order(cr, uid, ids,
                                                            context=context)
        lcp_pool.write(cr, uid, line_ids, {'active': True})
        return res

    def _landed_cost_base_volume(self, cr, uid, ids, name, args, context=None):
        '''get total cost based on volume'''
        if not ids:
            return {}
        result = {}
        landed_costs_base_volume = 0.0
        for order in self.browse(cr, uid, ids, context=context):
            if order.landed_cost_line_ids:
                for costs in order.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'volume' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_volume += costs.amount
            result[order.id] = landed_costs_base_volume
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        '''rewrite this to add a new type based on volume'''
        if not ids:
            return {}
        result = {}
        landed_costs = 0.0
        # landed costs for the purchase orders
        for order in self.browse(cr, uid, ids, context=context):
            landed_costs += (order.landing_cost_lines +
                             order.landed_cost_base_value +
                             order.landed_cost_base_quantity +
                             order.landed_cost_base_volume +
                             order.amount_untaxed)
            result[order.id] = landed_costs
        return result

    def _volume_total(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for order in self.browse(cr, uid, ids, context=context):
            volume_total = 0.0
            if order.order_line:
                for pol in order.order_line:
                    if pol.line_volume > 0.0:
                        volume_total += pol.line_volume
            result[order.id] = volume_total
        return result

    def _quantity_total(self, cr, uid, ids, name, args, context=None):
        '''calculate the total quantity of the pruducts
        TOFIX: fix parent module: purchase_landed_costs's bug:
            variable:quantity_total should be inited in the loop!!
        '''
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            quantity_total = 0.0
            if line.order_line:
                for pol in line.order_line:
                    if pol.product_qty > 0.0:
                        quantity_total += pol.product_qty
            result[line.id] = quantity_total
        return result

    _columns = {
        'volume_total': fields.function(
            _volume_total,
            digits_compute=dp.get_precision('Volume Factor'),
            string="Total Volume"),
        'landed_cost': fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Total Untaxed'),
        'landed_cost_base_volume': fields.function(
            _landed_cost_base_volume,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Volume'),
        'shipment_id': fields.many2one('landed.costs.shipment', 'Shipment'),
        'quantity_total': fields.function(
            _quantity_total,
            digits_compute=dp.get_precision('Product UoM'),
            string='Total Quantity'),
    }


class landed_cost_distribution_type(orm.Model):
    """ This is a model to give how we should distribute the amount given
    for a landed costs. At the begining we use a selection field, but it
    was impossible to filter it depending on the context (in a line or
    on order). So we replaced it by this object, adding is_* method to
    deal with. Base distribution are defined in YML file.

    We inehrit this model, add a new distribution type 'volume' to it.

    """

    _inherit = "landed.cost.distribution.type"

    _columns = {
        'landed_cost_type': fields.selection(
            [('value', 'Value'),
             ('per_unit', 'Quantity'),
             ('volume', 'Volume')],
            'Product Landed Cost Type',
            help="Refer to the product landed cost type."),
    }


class purchase_order_line(orm.Model):
    _inherit = "purchase.order.line"

    def _landing_cost(self, cr, uid, ids, name, args, context=None):
        '''rewrite this method to add a new distribution type'''
        if not ids:
            return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs = 0.0
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    # based on product value
                    if (costs.distribution_type_id.landed_cost_type == 'value' and
                            costs.distribution_type_id.apply_on == 'line'):
                        landed_costs += costs.amount
                    # based on product volume
                    elif (costs.distribution_type_id.landed_cost_type == 'volume' and
                            costs.distribution_type_id.apply_on == 'line'):
                        landed_costs += line.line_volume * costs.amount
                    # based on product qty
                    else:
                        landed_costs += costs.amount * line.product_qty
            result[line.id] = landed_costs
        return result

    def _line_volume(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            volume_factor = line.product_uom and line.product_uom.volume_factor or 1.0
            res[line.id] = volume_factor * line.product_qty
        return res

    def _landing_cost_order(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        # Landed costs line by line
        for line in lines:
            landed_costs = 0.0
            order = line.order_id
            # distribution of landed costs of PO
            if order.landed_cost_line_ids:
                # Base value (Absolute Value)
                if order.landed_cost_base_value:
                    try:
                        landed_costs += (order.landed_cost_base_value /
                                         order.amount_untaxed *
                                         line.price_subtotal)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        pass
                # Base quantity (Per Quantity)
                if order.landed_cost_base_quantity:
                    try:
                        landed_costs += (order.landed_cost_base_quantity /
                                         order.quantity_total *
                                         line.product_qty)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        pass
                # Base Volume (Per Volume)
                if order.landed_cost_base_volume:
                    try:
                        landed_costs += (order.landed_cost_base_volume /
                                         order.volume_total *
                                         line.line_volume)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        pass
            result[line.id] = landed_costs
        return result
    _columns = {
        'line_volume': fields.function(
            _line_volume,
            string="Product CBM"),
        'landing_costs_order': fields.function(
            _landing_cost_order,
            digits_compute=dp.get_precision('Account'),
            string='Landing Costs from Order'),
        'landing_costs': fields.function(
            _landing_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landing Costs'),
    }


class product_uom(orm.Model):
    _inherit = 'product.uom'

    _columns = {
        'volume_factor': fields.float(
            'Volume Factor',
            digits_compute=dp.get_precision('Volume Factor'))
    }

    _defaults = {
        'volume_factor': 1.0
    }


class product_template(orm.Model):
    _inherit = "product.template"

    _columns = {
        'landed_cost_type': fields.selection(
            [('value', 'Value'),
             ('per_unit', 'Quantity'),
             ('volume', 'Volume'),
             ('none', 'None')],
            'Distribution Type',
            help="Used if this product is landed costs: "
                 "If landed costs are defined for purchase orders or pickings, "
                 "this indicates how the costs are distributed to the lines"),
    }
