# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from tools.translate import _

import openerp.addons.decimal_precision as dp

import time
from product._common import rounding


class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"

    def _price_field_get(self, cr, uid, context=None):
        result = super(product_pricelist_item, self)._price_field_get(cr, uid, context=context)

        result.append((-3, _('Fix Price based on UoP')))
        return result

    _columns = {
        'base': fields.selection(_price_field_get, 'Based on',required=True, size=-1, help="Base price for computation."),
        'uom_id': fields.many2one('product.uom','UoM for Fix Price',store=True),
    }
    _defaults = {
        'price_discount': lambda *a: -1,
        'base': lambda *a: -3,
    }

    def product_id_change(self,cr,uid,ids,product_id,context=None):
        if not product_id:
            return{}
        prod = self.pool.get('product.product').browse(cr,uid,product_id,context=context)

        if prod.default_code:
            return {'value': {'name': prod.default_code,'uom_id': prod.uom_po_id.id}}
        return{}     

    def create(self,cr,uid,vals,context=None):
        if not vals.get('uom_id',False) and vals.get('product_id', False) and vals.get('base',False) == -3:
            prod = self.pool.get('product.product').browse(cr,uid,vals.get('product_id',False),context=context)
            vals['uom_id'] = prod.uom_po_id.id

        return super(product_pricelist_item,self).create(cr,uid,vals,context=context) 

    def write(self, cr, uid, ids, vals, context=None):
        if type(ids) != type([]):
            ids = [ids]
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

    #def price_get_multi(self, cr, uid, product_ids, context=None):
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
        #products = dict([(item['id'], item) for item in product_obj.read(cr, uid, product_ids, ['categ_id', 'product_tmpl_id', 'uos_id', 'uom_id'])])
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

                #And
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



class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"
    
    def _qty_uop(self, cr, uid, ids, name, arg, context=None):
        res = {}
        
        uom_obj = self.pool.get('product.uom')     
        for id in ids:
            res.setdefault(id, 0.0)
        for product in self.browse(cr, uid, ids):
            res[product.id] = uom_obj._compute_qty(cr, uid, product.uom_id.id, product.qty_available, product.uom_po_id.id)
        return res

    def _amount_uom(self, cr, uid, ids, name, arg, context=None):
        res = {}

        for id in ids:
            res.setdefault(id, 0.0)
        for product in self.browse(cr, uid, ids):
            res[product.id] = product.qty_available * product.standard_price
        return res

    _columns = {
        #'price_uop': fields.float('Purchase Price(UoP)', digits_compute=dp.get_precision('Product Price')),
        'qty_uop': fields.function(_qty_uop, type='float', string='Qty on Hand (UoP)', digits_compute=dp.get_precision('Product Unit of Measure')),
        'amount_uom': fields.function(_amount_uom, type='float', string='Stock Values', digits_compute=dp.get_precision('Account')),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if type(ids) != type([]):
            ids = [ids]
        if vals.get('uom_po_id', False) and ids:
            uom_obj = self.pool.get('product.uom')
            uop = uom_obj.browse(cr, uid, vals.get('uom_po_id', False), context=context)
            pl_item_obj = self.pool.get('product.pricelist.item')
            pl_ids = pl_item_obj.search(cr, uid, [('product_id', '=', ids[0]), ('base', '=', -3)], context=context)
            for item in pl_item_obj.browse(cr, uid, pl_ids, context=context):
                if item.uom_id and uop.id == item.uom_id.id:
                    continue
                new_price = item.price_surcharge / uop.factor * item.uom_id.factor
                pl_item_obj.write(cr, uid, [item.id], {'uom_id': vals.get('uom_po_id', False), 'price_surcharge': new_price})
        
        return super(product_product, self).write(cr, uid, ids, vals, context=context)    

product_product()