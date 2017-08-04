# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

from openerp.addons.product_price_history.product_price_history import PRODUCT_FIELD_HISTORIZE
PRODUCT_FIELD_HISTORIZE.extend(['duty_paid_cost', 'duty_free_cost', 'transit_cost'])


class product_duty_rule(orm.Model):
    _name = 'product.duty.rule'

    _columns = {
        'name': fields.char('Name', size=256, required=True, readonly=False),
        'company_id': fields.many2one('res.company', 'Company', required=False),
        'partner_id': fields.many2one(
            'res.partner', 'Default Supplier',
            domain=[('supplier', '=', True)],
            required=True),
        'active': fields.boolean(
            'Active',
            help="If the active field is set to false, "
                 "it will allow you to hide the duty rule without removing it."),
        'src_location_id': fields.many2one(
            'stock.location', 'Source location',
            domain=[('duty_zone_id', '!=', False)],
            help="if the source location of the stock move matches this location, "
                 "we use this rule to generate landed cost for the stock move."),
        'dest_location_id': fields.many2one(
            'stock.location', "Destination location",
            domain=[('duty_zone_id', '!=', False)],
            help="if the destination location of the stock move matches this location, "
                 "we use this rule to generate the landed cost for the stock move"),
        'generate_invoice': fields.boolean(
            'Generate Invoice',
            help="If ticked, this will generate a draft invoice at the "
                 "stock move confirmation for this landed cost position from the "
                 "related partner. If not, no invoice will be generated, "
                 "but the cost will still be included for the average price "
                 "computation."),
        'amount_select': fields.selection(
            [('percentage', 'Percentage (%)'),
             ('fix', 'Fixed Amount'),
             ('code', 'Python Code')],
            'Amount Type', select=True, required=True,
            help="The computation method for the rule amount."),
        'amount_fix': fields.float(
            'Fixed Amount', digits_compute=dp.get_precision('Landed Costs'),),
        # TODO give an example in the help message.
        'quantity': fields.char(
            'Quantity', size=256,
            help="It is used in computation for percentage and fixed amount."),
        'amount_percentage': fields.float(
            'Percentage (%)', digits_compute=dp.get_precision('Duty Rate'),
            help='For example, enter 50.0 to apply a percentage of 50%'),
        'amount_python_compute': fields.text('Python Code'),
        'amount_percentage_base': fields.char(
            'Percentage based on', size=1024, required=False,
            readonly=False, help='result will be affected to a variable'),
        'note': fields.text('Description'),
        # TODO how does this field work, details should be filled into the help message.
        'currency_id': fields.many2one(
            'res.currency', 'Currency',
            help="Default value would be current company default currency."
            "This currency would be passed to the according landed cost."),
        'product_id': fields.many2one(
            'product.product',
            'Landed Cost Name',
            required=True,
            domain=[('landed_cost_type', '!=', False)]),
        'distribution_type_id': fields.many2one(
            'landed.cost.distribution.type',
            'Multiple Type',
            required=True,
            domain=[('apply_on', '=', 'line')],
            help="Defines if the amount is to be calculated for each quantity "
                 "or an absolute value, this will be passed to the according landed cost."),
        'invoice_total_per_product': fields.boolean(
            "Total Per Product",
            help="When we invoice for this landing cost, "
            "whether we only create one invoice for one picking."),
    }

    def _get_default_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.currency_id.id

    _defaults = {
        'active': True,

        'generate_invoice': True,
        'amount_percentage': 100,

        'currency_id': _get_default_currency,

        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid, c).company_id.id,

        'amount_python_compute': '''
# Available variables:
#----------------------
# product: object containing the product

# Note: returned value have to be set in the variable 'result'

result = product.standard_price * 0.10''',
    }


class product_template(orm.Model):
    _inherit = 'product.template'

    _columns = {
        # TODO decide the group of these two fields.
        'duty_free_cost': fields.float(
            'Duty Free Cost',
            digits_compute=dp.get_precision('Product Price'),
            help="The cost price of product to be updated and used for duty free zone"),
        'transit_cost': fields.float(
            'Transit Cost',
            digits_compute=dp.get_precision('Product Price'),
            help="The cost price of product to be updated and used for transit zone"),
        'duty_paid_cost': fields.float(
            'Duty Paid Cost',
            digits_compute=dp.get_precision('Product Price'),
            help="The cost price of product to be updated and used for duty free zone"),
        
    }


class product_product(orm.Model):
    _inherit = 'product.product'

    def _product_value(self, cr, uid, ids,
                       field_names=None, arg=False, context=None):
        """ Comute the value of product using qty_available and historize
        values for the price.
        @return: Dictionary of values

        inherit from module: product_price_history
        """
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = 0.0
        # get right field
        price_name = context.get('cost_type', 'standard_price')
        products = self.read(cr, uid, ids,
                             ['id', 'qty_available', price_name],
                             context=context)
        for product in products:
            res[product['id']] = product['qty_available'] * product[price_name]
        return res

    _columns = {
        'value_available': fields.function(
            _product_value,
            type='float', digits_compute=dp.get_precision('Product Price'),
            group_operator="sum",
            string='Value',
            help="Current value of products available.\n"
                 "This is using the product historize price."
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children."),
        'duty_rule_ids': fields.many2many(
            'product.duty.rule', 'product_duty_rule_product_rel',
            'product_id', 'rule_id', 'Landing Costs Rules'),
    }

    def _get_duty_zone(self, cr, uid, price_name, context=None):
        '''Get the duty zone with the cost price(param: price_name)

        :return: the id of duty zone or False'''
        # TODO unit test on this function.
        # FIXME: what if the constraint(one duty zone per (company, price)) changes.
        # get the price type
        price_type_obj = self.pool.get('product.price.type')
        price_type_ids = price_type_obj.search(
            cr, uid, [('field', '=', price_name)], context=context)
        # get the duty zone with this price type.
        if price_type_ids:
            duty_zone_obj = self.pool.get('stock.duty.zone')
            duty_zone_ids = duty_zone_obj.search(
                cr, uid, [('price_type_id', '=', price_type_ids[0])],
                context=context)
            return duty_zone_ids and duty_zone_ids[0] or False
        return False

    def get_zone_from_cost_name(self, cr, uid, field_name, context=None):
        '''Get the duty zone from cost name
        :return: browse_record object of stock.duty.zone'''
        zone_obj = self.pool.get('stock.duty.zone')
        zone_ids = zone_obj.search(
            cr, uid,
            [('price_type_id.field', '=', field_name)], context=context)
        assert len(zone_ids) < 2, 'There is more than one zone in the company '
        'share the same cost price.'
        if not zone_ids:
            raise osv.except_osv(
                _('Warning!'),
                _('There is no duty zone for the cost price: %s' % field_name))
        zone = zone_obj.browse(cr, uid, zone_ids[0], context=context)
        return zone

    def do_change_cost_price(self, cr, uid, ids, datas, field_name, context=None):
        """ Changes the cost Prices (eg duty zone cost/ duty free cost) of Product
        and creates an account move accordingly.
        @param field_name: later on if we add a new cost price, we can still use this function.
        @param datas : dict. contain default datas like new_price,
        stock_output_account, stock_input_account, stock_journal
        @param context: A standard dictionary
        @return:

        """
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        duty_zone_obj = self.pool.get('stock.duty.zone')
        if context is None:
            context = {}

        new_price = datas.get('new_price', 0.0)
        stock_output_acc = datas.get('stock_output_account', False)
        stock_input_acc = datas.get('stock_input_account', False)
        journal_id = datas.get('stock_journal', False)
        product_obj = self.browse(cr, uid, ids, context=context)[0]
        # This valuatoin account is from duty zone.
        account_valuation_id = datas.get('stock_valuation_account', False)
        if not account_valuation_id:
            account_valuation = product_obj.categ_id.property_stock_valuation_account_id
            account_valuation_id = account_valuation and account_valuation.id or False
        if not account_valuation_id:
            raise osv.except_osv(
                _('Error!'),
                _('Specify valuation Account for the according duzy zone or the product category!'))
        move_ids = []
        # get the company_id
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        # get the duty zone.
        duty_zone_id = self._get_duty_zone(cr, uid, field_name, context=context)
        if not duty_zone_id:
            raise osv.except_osv(
                _('warning!'),
                _('Please assign the price: %s to a duty zone for this price.') % field_name)
        duty_zone = duty_zone_obj.browse(cr, uid, duty_zone_id, context=context)

        # we only get the locations from the specific duty zone.
        loc_ids = location_obj.search(
            cr, uid,
            [('usage', '=', 'internal'), ('company_id', 'in', (company_id, False)),
             ('active', '=', True), ('duty_zone_id', '=', duty_zone_id)])
        for rec_id in ids:
            for location in location_obj.browse(cr, uid, loc_ids, context=context):
                c = context.copy()
                c.update({
                    'location': location.id,
                    'compute_child': False
                })

                product = self.browse(cr, uid, rec_id, context=c)
                #Note the uom of qty_available is the same as default uom
                qty = product.qty_available
                try:
                    cost_price = getattr(product, field_name)
                except:
                    raise osv.except_osv(
                        _('warning'),
                        _('Cannot get the product cost price with name: %s' % field_name))
                diff = cost_price - new_price
                if not diff:
                    raise osv.except_osv(
                        _('Error!'),
                        _("No difference between standard price and new price!"))
                if qty > 0:
                    company_id = location.company_id and location.company_id.id or False
                    if not company_id:
                        raise osv.except_osv(
                            _('Error!'),
                            _('Please specify company in Location.'))
                    #
                    # Accounting Entries
                    #
                    journal_id = duty_zone.journal_id.id
                    if not journal_id:
                        journal_id = product.categ_id.property_stock_journal and \
                            product.categ_id.property_stock_journal.id or False
                    if not journal_id:
                        raise osv.except_osv(
                            _('Error!'),
                            _('Please define journal '
                              'on the product category: "%s" (id: %d).') % (product.categ_id.name,
                                    product.categ_id.id,))
                    move_id = move_obj.create(cr, uid, {
                                'journal_id': journal_id,
                                'company_id': company_id
                                })

                    move_ids.append(move_id)

                    if diff > 0:
                        if not stock_input_acc:
                            stock_input_acc = product.\
                                property_stock_account_input.id
                        if not stock_input_acc:
                            stock_input_acc = product.categ_id.\
                                    property_stock_account_input_categ.id
                        if not stock_input_acc:
                            raise osv.except_osv(_('Error!'),
                                    _('Please define stock input account ' \
                                            'for this product: "%s" (id: %d).') % \
                                            (product.name,
                                                product.id,))
                        amount_diff = qty * diff
                        move_line_obj.create(cr, uid, {
                                    'name': product.name,
                                    'account_id': stock_input_acc,
                                    'debit': amount_diff,
                                    'credit': 0,
                                    'move_id': move_id,
                                    'partner_id': False
                                    })
                        move_line_obj.create(cr, uid, {
                                    'name': product.categ_id.name,
                                    'account_id': account_valuation_id,
                                    'credit': amount_diff,
                                    'debit': 0,
                                    'move_id': move_id,
                                    'partner_id': False
                                    })
                    elif diff < 0:
                        if not stock_output_acc:
                            stock_output_acc = product.\
                                property_stock_account_output.id
                        if not stock_output_acc:
                            stock_output_acc = product.categ_id.\
                                    property_stock_account_output_categ.id
                        if not stock_output_acc:
                            raise osv.except_osv(_('Error!'),
                                    _('Please define stock output account ' \
                                            'for this product: "%s" (id: %d).') % \
                                            (product.name,
                                                product.id,))
                        amount_diff = qty * -diff
                        move_line_obj.create(cr, uid, {
                                        'name': product.name,
                                        'account_id': stock_output_acc,
                                        'credit': amount_diff,
                                        'debit': 0,
                                        'move_id': move_id,
                                        'partner_id': False
                                    })
                        move_line_obj.create(cr, uid, {
                                        'name': product.categ_id.name,
                                        'account_id': account_valuation_id,
                                        'debit': amount_diff,
                                        'credit': 0,
                                        'move_id': move_id,
                                        'partner_id': False
                                    })
            self.write(cr, uid, rec_id, {field_name: new_price})

        return move_ids
