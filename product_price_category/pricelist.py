# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from _common import rounding
import time


class product_pricelist(osv.osv):
    _inherit = 'product.pricelist'
    _name    = 'product.pricelist'
    _description = "Pricelist"
    
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
        
                
        def _create_parent_pricecategory_list(id, lst):
            if not id:
                return []
            parent = product_pricecategory_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_pricecategory_list(parent, lst)
            else:
                return lst
        
        
        if context is None:
            context = {}
        
        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']
        
        currency_obj         = self.pool.get('res.currency')
        product_obj          = self.pool.get('product.product')
        product_template_obj = self.pool.get('product.template')
        product_category_obj = self.pool.get('product.category')
        product_uom_obj      = self.pool.get('product.uom')
        supplierinfo_obj     = self.pool.get('product.supplierinfo')
        price_type_obj       = self.pool.get('product.price.type')
        product_pricecategory_obj     = self.pool.get('product.pricecategory')
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')
        
        # product.pricelist.version:
        if pricelist_ids:
            pricelist_version_ids = pricelist_ids
        else:
            # all pricelists:
            pricelist_version_ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)
        
        pricelist_version_ids  = list(set(pricelist_version_ids))
        plversions_search_args = [
            ('pricelist_id', 'in', pricelist_version_ids),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ]
        
        plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
        if len(pricelist_version_ids) != len(plversion_ids):
            raise osv.except_osv(_('Warning !'), _("At least one pricelist has no active version !\nPlease create or activate one."))
        
        # product.product:
        product_ids   = [i[0] for i in products_by_qty_by_partner]
        #products      = dict([(item['id'], item) for item in product_obj.read(cr, uid, product_ids, ['categ_id', 'product_tmpl_id', 'uos_id', 'uom_id'])])
        products      = product_obj.browse(cr, uid, product_ids, context=context)
        products_dict = dict([(item.id, item) for item in products])
        
        # product.category:
        product_category_ids  = product_category_obj.search(cr, uid, [])
        product_categories    = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])
                
        product_pricecategory_ids  = product_pricecategory_obj.search(cr, uid, [])
        product_pricecategories    = product_category_obj.read(cr, uid, product_pricecategory_ids, ['parent_id'])
        product_pricecategory_tree = dict([(item['id'], item['parent_id'][0]) for item in product_pricecategories if item['parent_id']])      
        
        results = {}
        for product_id, qty, partner in products_by_qty_by_partner:
            for pricelist_id in pricelist_version_ids:
                price     = False
                tmpl_id   = products_dict[product_id].product_tmpl_id and products_dict[product_id].product_tmpl_id.id or False
                categ_id  = products_dict[product_id].categ_id and products_dict[product_id].categ_id.id or False
                categ_ids = _create_parent_category_list(categ_id, [categ_id])
                
                if categ_ids:
                    categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                else:
                    categ_where = '(categ_id IS NULL)'                    
                
                #jon pricecategory_ids comes from product.price_category_id
                # why need function _create_parent_pricecategory_list?  
                pricecategory_ids = None
                p = products_dict[product_id]
                if p.pricecategory_id:
                    pricecategory_ids = [p.pricecategory_id.id]
                
                if pricecategory_ids:
                    # jon search pricelist_item , pricecategory_id == product.pricecategory_id or  pricecategory_id == False 
                    pricecateg_where = '(pricecategory_id IN (' + ','.join(map(str, pricecategory_ids)) + ') OR pricecategory_id IS NULL)'
                else:
                    pricecateg_where = '(pricecategory_id IS NULL)'
                
                cr.execute(
                    'SELECT i.*, pl.currency_id '
                    'FROM product_pricelist_item AS i, '
                        'product_pricelist_version AS v, product_pricelist AS pl '
                    'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %s) '
                        'AND (product_id IS NULL OR product_id = %s) '
                        'AND (' + categ_where + ' OR (categ_id IS NULL)) '
                        # 'AND (' + pricecateg_where + ' OR (pricecategory_id IS NULL)) '
                        'AND (' + pricecateg_where + ')'
                        'AND price_version_id = %s '
                        'AND (min_quantity IS NULL OR min_quantity <= %s) '
                        'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
                    'ORDER BY i.pricecategory_id ,sequence',
                    (tmpl_id, product_id, plversion_ids[0], qty))
                res1 = cr.dictfetchall()
                uom_price_already_computed = False
                
                for res in res1:
                    if res:
                        if res['base'] == -1:
                            if not res['base_pricelist_id']:
                                price = 0.0
                            else:
                                price_tmp = self.price_get(cr, uid, [res['base_pricelist_id']], product_id, qty, context=context)[res['base_pricelist_id']]
                                ptype_src = self.browse(cr, uid, res['base_pricelist_id']).currency_id.id
                                price     = currency_obj.compute(cr, uid, ptype_src, res['currency_id'], price_tmp, round=False)
                        
                        elif res['base'] == -2:
                            # this section could be improved by moving the queries outside the loop:
                            where = []
                            if partner:
                                where = [('name', '=', partner) ]
                            sinfo = supplierinfo_obj.search(cr, uid, [('product_id', '=', tmpl_id)] + where)
                            price = 0.0
                            if sinfo:
                                qty_in_product_uom  = qty
                                product_default_uom = product_template_obj.read(cr, uid, [tmpl_id], ['uom_id'])[0]['uom_id'][0]
                                supplier            = supplierinfo_obj.browse(cr, uid, sinfo, context=context)[0]
                                seller_uom          = supplier.product_uom and supplier.product_uom.id or False
                                supplier_currency   = supplier.company_id and supplier.company_id.currency_id.id or False
                                
                                if seller_uom and product_default_uom and product_default_uom != seller_uom:
                                    uom_price_already_computed = True
                                    qty_in_product_uom = product_uom_obj._compute_qty(cr, uid, product_default_uom, qty, to_uom_id=seller_uom)
                                cr.execute("""  SELECT *
                                                FROM pricelist_partnerinfo
                                                WHERE suppinfo_id IN %s
                                                  AND min_quantity <= %s
                                                ORDER BY min_quantity DESC LIMIT 1 """, (tuple(sinfo),qty_in_product_uom,))
                                res2 = cr.dictfetchone()
                                if res2:
                                    price = currency_obj.compute(cr, uid, supplier_currency, res['currency_id'], res2['price'], round=False, context=context)
                        else:
                            price_type = price_type_obj.browse(cr, uid, int(res['base']))
                            price      = currency_obj.compute(cr, uid,
                                                              price_type.currency_id.id, res['currency_id'],
                                                              product_obj.price_get(cr, uid, [product_id], price_type.field,context=context)[product_id], round=False, context=context)
                            
                            uom_price_already_computed = True    
                        
                        if price is not False:
                            price_limit = price
                            price  = price * (1.0 + (res['price_discount'] or 0.0))
                            price  = rounding(price, res['price_round'])
                            price += (res['price_surcharge'] or 0.0)
                            if res['price_min_margin']:
                                price = max(price, price_limit + res['price_min_margin'])
                            if res['price_max_margin']:
                                price = min(price, price_limit + res['price_max_margin'])
                            break
                    
                    else:
                        # False means no valid line found ! But we may not raise an
                        # exception here because it breaks the search
                        price = False
                
                if price:
                    if 'uom' in context and not uom_price_already_computed:
                        product = products_dict[product_id]
                        uom     = product.uos_id or product.uom_id
                        price   = self.pool.get('product.uom')._compute_price(cr, uid, uom.id, price, context['uom'])
                
                if results.get(product_id):
                    results[product_id][pricelist_id] = price
                else:
                    results[product_id] = {pricelist_id: price}
        return results

product_pricelist()



class product_pricelist_item(osv.osv):
    _inherit = 'product.pricelist.item'
    _name    = 'product.pricelist.item'
    _description = "Pricelist item"
    
    def _get_default_price_type(self, cr, uid, context=None):
        selection     = self._price_field_get(cr, uid, context=None)
        price_type_id = -1
        for id_name in selection:
            if id_name[1] == 'Sale Price':
                price_type_id = id_name[0]
                break
        return price_type_id
    
    _columns = {
         'pricecategory_id': fields.many2one('product.pricecategory', 'pricecategory_id', ondelete='cascade', help="Set a category of price if this rule only apply to price of a category and his children. Keep empty for all products"),
    }
    
    #jon.chow<@>elico-corp.com    May 21, 2013
    _defaults = {
        'base': lambda self,cr,uid,context: self._get_default_price_type(cr,uid,context=context),   
    }

product_pricelist_item()

