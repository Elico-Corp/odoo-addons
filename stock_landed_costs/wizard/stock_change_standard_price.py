# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class change_standard_price(orm.TransientModel):
    _inherit = "stock.change.standard.price"
    _name = 'stock.change.standard.price'

    _columns = {
        'price_select': fields.selection(
            [('standard_price', 'Cost price'),
             ('duty_free_cost', 'Duty Free Price'),
             ('duty_paid_cost', 'Duty Paid Price'),
             ('transit_cost', "Transit Price")], 'Select Price', required=True,
            help="Select what kind of cost price you want to update."),

        #TODO to improve the help message of the three prices.
        'new_price': fields.float(
            'New Cost Price', digits_compute=dp.get_precision('Product Price'),
            help="If cost price is increased, stock variation account will be debited "
            "and stock output account will be credited with the value = "
            "(difference of amount * quantity available).\n"
            "If cost price is decreased, stock variation "
            "account will be creadited and stock input account will be debited."
            "This price doesn't include the the landed costs on the stock moves level."),
    }

    _defaults = {
        'price_select': 'standard_price',
    }

    def change_price(self, cr, uid, ids, context=None):
        """ Changes the Standard Price of Product.
            And creates an account move accordingly.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context.')
        prod_obj = self.pool.get('product.product')
        res = self.browse(cr, uid, ids, context=context)
        datas = {
            'new_price': res[0].new_price,
            'stock_output_account': res[0].stock_account_output.id,
            'stock_input_account': res[0].stock_account_input.id,
            'stock_journal': res[0].stock_journal.id
        }
        select = res[0].price_select
        if select == 'standard_price':
            # we keep standard odoo behavior.
            prod_obj.do_change_standard_price(cr, uid, [rec_id], datas, context)
        else:
            # update the stock valuation account.
            zone = prod_obj.get_zone_from_cost_name(cr, uid, select, context=context)
            datas['stock_valuation_account'] = zone.val_account_id.id
            prod_obj.do_change_cost_price(cr, uid, [rec_id], datas, select, context)
        return {'type': 'ir.actions.act_window_close'}

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        #TODO the default stock input/output account, stock journal
        # check if there is any specific need.
        return super(change_standard_price, self).default_get(
            cr, uid, fields, context=context)


class stock_set_locations_duty_zone(orm.TransientModel):
    _name = "stock.set.locations.duty.zone"

    _columns = {
        'location_ids': fields.many2many(
            'stock.location', 'set_location_duty_zone_location_rel',
            'set_id', 'location_id', 'Locations',
            domain=[('usage', '=', 'internal'), ('duty_zone_id', '=', False)])
    }

    def assign_locations(self, cr, uid, ids, context=None):
        location_obj = self.pool.get('stock.location')
        for assigner in self.browse(cr, uid, ids, context=context):
            location_ids = [location.id for location in assigner.location_ids]
            if context and context.get('active_id', False):
                # assign the locations to the duty zone
                for loc in location_obj.browse(cr, uid, location_ids, context=context):
                    loc.write({'duty_zone_id': context.get('active_id')})
        return {'type': 'ir.actions.act_window_close'}
