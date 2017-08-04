# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import time
from product._common import rounding

from osv import osv, fields
from tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
from openerp.osv.orm import browse_record, browse_null


class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context and context.get('supplier_id', False):
            ids = []
            cr.execute("SELECT distinct(product_id) FROM product_supplierinfo where name = %s" % (context.get('supplier_id')))
            ids = [x[0] for x in cr.fetchall()]
            args.append(('id','in',ids))
            order = 'default_code'
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)


    _columns = {
        'po_price_modification_limit':fields.boolean("No control on PO price", help="""If checked, allows you to change the price in PO (only when either the Supplier or Product allow it)."""),
    }

    _defaults = {
        'po_price_modification_limit': True
    }
    
    #
    # Could be overrided for variants matrices prices
    #
    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = {}

        if 'currency_id' in context:
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(cr, uid, [('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(cr, uid, price_type_id).currency_id.id

        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = product[ptype] or 0.0
            if ptype == 'list_price':
                res[product.id] = (res[product.id] * (product.price_margin or 1.0)) + \
                        product.price_extra
                
            if 'uom' in context:
                uom = product.uom_id or product.uos_id
                if ptype == 'price_uop':
                    uom = product.uom_po_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, res[product.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                    context['currency_id'], res[product.id], context=context)

        return res    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('uom_po_id', False) and ids:
            uom_obj = self.pool.get('product.uom')
            uop = uom_obj.browse(cr, uid, vals.get('uom_po_id', False), context=context)
            pl_item_obj = self.pool.get('product.pricelist.item')
            pl_ids = pl_item_obj.search(cr, uid, [('product_id', '=', ids[0]), ('base', '=', -3)], context=context)
            for item in pl_item_obj.browse(cr, uid, pl_ids, context=context):
                if uop.id == item.uom_id.id:
                    continue
                new_price = item.price_surcharge / uop.factor * item.uom_id.factor
                pl_item_obj.write(cr, uid, [item.id], {'uom_id': vals.get('uom_po_id', False), 'price_surcharge': new_price})

        return super(product_product, self).write(cr, uid, ids, vals, context=context)    

product_product()

class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"
    
    def _price_field_get(self, cr, uid, context=None):
        result = super(product_pricelist_item, self)._price_field_get(cr, uid, context=context)

        result.append((-3, _('Fix Price based on UoP')))
        return result

    _columns = {
        'base': fields.selection(_price_field_get, 'Based on', required=True, size= -1, help="Base price for computation."),
        'uom_id': fields.many2one('product.uom', 'UoM for Fix Price', store=True),
    }
    
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        
        if prod.default_code:
            return {'value': {'name': prod.default_code, 'uom_id': prod.uom_po_id.id}}
        return {}

    def create(self, cr, uid, vals, context=None):
        if not vals.get('uom_id', False) and vals.get('product_id', False) and vals.get('base', False) == -3:
            prod = self.pool.get('product.product').browse(cr, uid, vals.get('product_id', False), context=context)
            vals['uom_id'] = prod.uom_po_id.id
                
        return super(product_pricelist_item, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('uom_id', False) and ids:            
            pl_item_obj = self.pool.get('product.pricelist.item')
            for id in ids:
                item = pl_item_obj.browse(cr, uid, id, context=context)
                if item.base == -3 and item.product_id:
                    vals['uom_id'] = item.product_id.uom_po_id.id
        return super(product_pricelist_item, self).write(cr, uid, ids, vals, context=context)     
product_pricelist_item()

class product_pricelist(osv.osv):
    _inherit = "product.pricelist"


    def price_get_multi(self, cr, uid, pricelist_ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param pricelist_ids:
           @param products_by_qty:
           @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
        """

        def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst
        # _create_parent_category_list

        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']

        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.product')
        product_category_obj = self.pool.get('product.category')
        product_uom_obj = self.pool.get('product.uom')
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        price_type_obj = self.pool.get('product.price.type')

        # product.pricelist.version:
        if not pricelist_ids:
            pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)

        pricelist_version_ids = self.pool.get('product.pricelist.version').search(cr, uid, [
                                                        ('pricelist_id', 'in', pricelist_ids),
                                                        '|',
                                                        ('date_start', '=', False),
                                                        ('date_start', '<=', date),
                                                        '|',
                                                        ('date_end', '=', False),
                                                        ('date_end', '>=', date),
                                                    ])
        if len(pricelist_ids) != len(pricelist_version_ids):
            raise osv.except_osv(_('Warning!'), _("At least one pricelist has no active version !\nPlease create or activate one."))

        # product.product:
        product_ids = [i[0] for i in products_by_qty_by_partner]
        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_dict = dict([(item.id, item) for item in products])

        # product.category:
        product_category_ids = product_category_obj.search(cr, uid, [])
        product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

        results = {}
        for product_id, qty, partner in products_by_qty_by_partner:
            for pricelist_id in pricelist_ids:
                price = False

                tmpl_id = products_dict[product_id].product_tmpl_id and products_dict[product_id].product_tmpl_id.id or False

                categ_id = products_dict[product_id].categ_id and products_dict[product_id].categ_id.id or False
                categ_ids = _create_parent_category_list(categ_id, [categ_id])
                if categ_ids:
                    categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                else:
                    categ_where = '(categ_id IS NULL)'

                if partner:
                    partner_where = 'base <> -2 OR %s IN (SELECT name FROM product_supplierinfo WHERE product_id = %s) '
                    partner_args = (partner, tmpl_id)
                else:
                    partner_where = 'base <> -2 '
                    partner_args = ()

                pl = self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context) 
                if pl.type == "purchase":
                    product = products_dict[product_id]
                    if 'uom' in context:
                        uom = product.uom_po_id
                        if uom.id != context['uom']:
                            qty = qty * product.uom_po_id.factor / product.uom_id.factor

                cr.execute(
                    'SELECT i.*, pl.currency_id '
                    'FROM product_pricelist_item AS i, '
                        'product_pricelist_version AS v, product_pricelist AS pl '
                    'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %s) '
                        'AND (product_id IS NULL OR product_id = %s) '
                        'AND (' + categ_where + ' OR (categ_id IS NULL)) '
                        'AND (' + partner_where + ') '
                        'AND price_version_id = %s '
                        'AND (min_quantity IS NULL OR min_quantity <= %s) '
                        'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
                    'ORDER BY sequence',
                    (tmpl_id, product_id) + partner_args + (pricelist_version_ids[0], qty))
                res1 = cr.dictfetchall()
                uom_price_already_computed = False
                for res in res1:
                    if res:
                        if res['base'] == -1:
                            if not res['base_pricelist_id']:
                                price = 0.0
                            else:
                                price_tmp = self.price_get(cr, uid,
                                        [res['base_pricelist_id']], product_id,
                                        qty, context=context)[res['base_pricelist_id']]
                                ptype_src = self.browse(cr, uid, res['base_pricelist_id']).currency_id.id
                                uom_price_already_computed = True
                                price = currency_obj.compute(cr, uid, ptype_src, res['currency_id'], price_tmp, round=False)
                        elif res['base'] == -2:
                            # this section could be improved by moving the queries outside the loop:
                            where = []
                            if partner:
                                where = [('name', '=', partner) ]
                            sinfo = supplierinfo_obj.search(cr, uid,
                                    [('product_id', '=', tmpl_id)] + where)
                            price = 0.0
                            if sinfo:
                                qty_in_product_uom = qty
                                product_default_uom = product_obj.read(cr, uid, [product_id], ['uom_id'])[0]['uom_id'][0]
                                supplier = supplierinfo_obj.browse(cr, uid, sinfo, context=context)[0]
                                seller_uom = supplier.product_uom and supplier.product_uom.id or False
                                if seller_uom and product_default_uom and product_default_uom != seller_uom:
                                    uom_price_already_computed = True
                                    qty_in_product_uom = product_uom_obj._compute_qty(cr, uid, product_default_uom, qty, to_uom_id=seller_uom)
                                cr.execute('SELECT * ' \
                                        'FROM pricelist_partnerinfo ' \
                                        'WHERE suppinfo_id IN %s' \
                                            'AND min_quantity <= %s ' \
                                        'ORDER BY min_quantity DESC LIMIT 1', (tuple(sinfo), qty_in_product_uom,))
                                res2 = cr.dictfetchone()
                                if res2:
                                    price = res2['price']
                        #Add by Andy
                        elif res['base'] == -3:
                            price = False
                        else:
                            price_type = price_type_obj.browse(cr, uid, int(res['base']))
                            uom_price_already_computed = True
                            price = currency_obj.compute(cr, uid,
                                    price_type.currency_id.id, res['currency_id'],
                                    product_obj.price_get(cr, uid, [product_id],
                                    price_type.field, context=context)[product_id], round=False, context=context)

                        if price is not False:
                            price_limit = price
                            price = price * (1.0 + (res['price_discount'] or 0.0))
                            price = rounding(price, res['price_round']) #TOFIX: rounding with tools.float_rouding
                            price += (res['price_surcharge'] or 0.0)
                            if res['price_min_margin']:
                                price = max(price, price_limit + res['price_min_margin'])
                            if res['price_max_margin']:
                                price = min(price, price_limit + res['price_max_margin'])
                            break
                        #Add by Andy
                        else:        
                            if res['base'] == -3:
                                price = res['price_surcharge'] or 0.0                                    
                                product = products_dict[product_id]
                                if 'uom' in context:
                                    uom = product.uom_po_id
                                    if uom.id != context['uom']:
                                        price = product_uom_obj._compute_price(cr, uid, uom.id, price, context['uom'])
                                uom_price_already_computed = True
                                #Todo: # Use company currency?
                                if 'currency_id' in context:                                    
                                    price = currency_obj.compute(cr, uid, 1,
                                        context['currency_id'], price, context=context)
                                if price:
                                    break
                    else:
                        # False means no valid line found ! But we may not raise an
                        # exception here because it breaks the search
                        price = False

                if price:
                    results['item_id'] = res['id']
                    if 'uom' in context and not uom_price_already_computed:
                        product = products_dict[product_id]
                        uom = product.uos_id or product.uom_id
                        price = product_uom_obj._compute_price(cr, uid, uom.id, price, context['uom'])

                if results.get(product_id):
                    results[product_id][pricelist_id] = price
                else:
                    results[product_id] = {pricelist_id: price}

        return results

product_pricelist()

def add_sequence(lines):
    for line in lines:
        if line[0] != 2:#line[2]:#and line[2].get('sequence',False)
            if line[2]:
                line[2].update({'sequence': lines.index(line) + 1})
            else:
                line[2] = {'sequence': lines.index(line) + 1}
                line[0] = 1
    return lines

def get_contact(obj, cr, uid, ids, location_id, dest_customer, company_id):
    partner_obj = obj.pool.get('res.partner')
    partner_id = False
    if dest_customer:
        partner = partner_obj.browser(cr, uid, dest_customer)
    elif location_id:
        loc_obj = obj.pool.get('stock.location')
        location = loc_obj.browse(cr, uid, location_id)
        if location and location.partner_id:
            partner = loc_obj.browser(cr, uid, location.partner_id.id)
    elif company_id:
        company_obj = obj.pool.get('res.company')
        company = company_obj.browse(cr, uid, company_id)
        partner = company.partner_id
    
    if partner:   
        if partner.parent_id:
            #Contact, return
            partner_id = partner.id
        elif partner.child_ids:
            #Company, if has contacts, return first one
            partner_id = partner.child_ids[0].id
        else:
            #Company, if has not contacts, return company directly.
            partner_id = partner.id
    return partner_id


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    _order = 'order_id desc, sequence'

    def _amount_line_with_tax(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, line.order_id.partner_id, force_excluded=True)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    def _qty_received(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            qty = 0.0
            for move in line.move_ids:
                if move.state == 'done':
                    qty += move.product_qty
            res[line.id] = qty
        return res
    
    def _qty_unreceived(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            qty = 0.0
            for move in line.move_ids:
                if move.state not in ('done', 'cancel'):
                    qty += move.product_qty
            res[line.id] = qty
        return res

    
    def onchange_price_unit(self, cr, uid, ids, partner_id, product_id, price_unit_original, price_unit, context=None):
        #Not use at the moment! add a readonly attribute in view definition!
        context = context or {}
        res = {}
        
        if not partner_id and not product_id:
            return res
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        
        #if purchase_config_settings.po_price_modification_limit:
        if not product.po_price_modification_limit and not partner.po_price_modification_limit and price_unit_original != price_unit:
            res['value'] = {'price_unit': price_unit_original or 0.0}
            res['warning'] = {'title' : _('PO Price'), 'message' : _('You can not modify the price of this product sold by this supplier !')}
            #raise osv.except_osv(_('Error!'), _('You can not modify the price of this product sold by this supplier !'))
        #ENDIF
        return res


    _columns = {
        'modify_price': fields.boolean('Modify Price'),
        'sequence': fields.integer('Sequence', help="Sequence for order in view and print report"),
        'amount_subtotal': fields.function(_amount_line_with_tax, string='Subtotal(Inc. Tax)', type='float', digits_compute=dp.get_precision('Account')),
        'qty_received': fields.function(_qty_received, string='Reception Qty', type='float', digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_unreceived': fields.function(_qty_unreceived, string='Waiting Qty', type='float', digits_compute=dp.get_precision('Product Unit of Measure')),
        'price_unit_original': fields.float('Original Unit Price', digits_compute= dp.get_precision('Product Price')),
    }
    _defaults = {
        'sequence': 1,
        'modify_price': False,
    }    
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)
        
        if not product_id or not partner_id:
            return res
        
        res_partner = self.pool.get('res.partner')
        partner = res_partner.browse(cr, uid, partner_id)
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id, context=context)
        
        modify_price = not product.po_price_modification_limit and not partner.po_price_modification_limit
        res['value'].update({'modify_price': modify_price})
        
        if res and 'value' in res and 'price_unit' in res['value']:
            res['value'].update({'price_unit_original': res['value']['price_unit']})
        
        name = product.name_en or ''
        if product.joomla_unit:
            name += "(%s)" % product.joomla_unit
        name += ' - ' + product.name_cn
        if product.joomla_unit:
            name += "(%s)" % product.joomla_unit_cn
        if product.description_purchase:
            name += '\n' + product.description_purchase
            
        res['value'].update({'name': name})
        return res

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def _get_default_delivery_id(self, cr, uid, context=None):
        if not warehouse_id:
            return False
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
        default_id = warehouse.lot_input_id.partner_id and warehouse.lot_input_id.partner_id.id or False
        return default_id
    
    _columns = {
        'delivery_id':fields.many2one('res.partner', 'Delivery', states={'done':[('readonly', True)]},),
        'contact_delivery_id':fields.many2one('res.partner', 'Delivery Contact', states={'done':[('readonly', True)]}),
        'contact_partner_id':fields.many2one('res.partner', 'Supplier Contact', states={'done':[('readonly', True)]}),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(purchase_order, self).default_get(cr, uid, fields,context)
        if res.get('warehouse_id',False):
            warehouse = self.pool.get('stock.warehouse').browse(cr, uid, res['warehouse_id'])
            delivery = warehouse.lot_input_id.partner_id.id or False
            res.update({'delivery_id':delivery})
        return res
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('order_line', False):
            vals['order_line'] = add_sequence(vals.get('order_line', []))
                
        return super(purchase_order, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('order_line', False):
            vals['order_line'] = add_sequence(vals.get('order_line', []))
        return super(purchase_order, self).write(cr, uid, ids, vals, context=context)

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        move = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context)
        move['sequence'] = order_line.sequence
        return move    

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id):
        if not warehouse_id:
            return {}
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
        vals = {'location_id': warehouse.lot_input_id.id, 'dest_address_id': False}
        if warehouse.lot_input_id.partner_id:
            loc_address = self.pool.get('res.partner').contact_get(cr, uid, [warehouse.lot_input_id.partner_id.id], ['default'])
            if loc_address:
                vals.update({'delivery_id': warehouse.lot_input_id.partner_id.id, 'contact_delivery_id': loc_address['default']})
        return {'value': vals}

    def onchange_location_id(self, cr, uid, ids, location_id):
        if not location_id:
            return {}
        loc_obj = self.pool.get('stock.location')
        partner = self.pool.get('res.partner')
        values = {'contact_delivery_id': False}
        location = loc_obj.browse(cr, uid, location_id)
        if location and location.partner_id:
            loc_address = partner.contact_get(cr, uid, [location.partner_id.id], ['default'])
            if loc_address:
                values.update({'contact_delivery_id': loc_address['default']})
        return {'value':values}

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        if not partner_id:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
                }}
        supplier_address = partner.contact_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        return {'value': {
            'pricelist_id': supplier.property_product_pricelist_purchase.id,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id': supplier.property_supplier_payment_term.id or False,
            'contact_partner_id': supplier_address and supplier_address['default'] or False
            }}
        
    def onchange_delivery_id(self, cr, uid, ids, partner_id):
        if not partner_id:
            return {'value': {
                'contact_delivery_id': False }}
            
        partner = self.pool.get('res.partner')
        supplier_address = partner.contact_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        return {'value': {            
            'contact_delivery_id': supplier_address and supplier_address['default'] or False
            }}
    
    def onchange_dest_address_id(self, cr, uid, ids, address_id):
        if not address_id:
            return {}
        address = self.pool.get('res.partner')
        values = {'warehouse_id': False}
        supplier = address.browse(cr, uid, address_id)
        if supplier:
            location_id = supplier.property_stock_customer.id
            values.update({'location_id': location_id, 'delivery_id': address_id})
        return {'value':values}
    
purchase_order()


class purchase_config_settings(osv.osv_memory):
    _name = 'purchase.config.settings'
    _inherit = 'purchase.config.settings'

    _columns = {
        'po_price_modification_limit':fields.boolean("Control on supplier/product PO price", help="""Allows you to change the price in PO, only when the supplier and Product allow it."""),
    }

    _defaults = {
        'po_price_modification_limit': True
    }
purchase_config_settings()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    _columns = {
        'po_price_modification_limit':fields.boolean("No control on PO price", help="""If checked, allows you to change the price in PO (only when either the Supplier or Product allow it)"""),
    }

    _defaults = {
        'po_price_modification_limit': True
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id:
                name = "%s (%s)" % (name, record.parent_id.name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n', '\n')
                name = name.replace('\n\n', '\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if context.get('show_phone') and record.phone:
                name = "%s <%s>" % (name, record.phone)
            if context.get('show_mobile'):
                name = "%s \n %s \n %s" % (name, record.mobile or record.phone,record.email)
            res.append((record.id, name))
        return res

    def contact_get(self, cr, uid, ids, adr_pref=None):
        if adr_pref is None:
            adr_pref = ['default']
        result = {}
        # retrieve addresses from the partner itself and its children
        res = []
        # need to fix the ids ,It get False value in list like ids[False]
        if ids and ids[0] != False:
            for p in self.browse(cr, uid, ids):
                res.extend((c.type, c.id) for c in p.child_ids)
        address_dict = dict(reversed(res))
        # get the id of the (first) default address if there is one,
        # otherwise get the id of the first address in the list
        default_address = False
        if res:
            default_address = address_dict.get('default', res[0][1])
        for adr in adr_pref:
            result[adr] = address_dict.get(adr, default_address)
        return result    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
