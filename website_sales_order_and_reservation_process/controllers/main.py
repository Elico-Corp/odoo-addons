# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import werkzeug

from openerp import SUPERUSER_ID, http
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import (QueryURL,
                                                          table_compute)
from openerp.http import request

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class WebsiteSale(website_sale):
    @http.route(
        ['/shop/check_stock_inventory'], type='json',
        auth="public", methods=['POST'], website=True
    )
    def check_stock_inventory(self, product_ids, add_qty, **kw):
        cr = request.cr
        context = request.context
        pool = request.registry

        product_obj = pool['product.product']

        products = product_obj.browse(
            cr, SUPERUSER_ID, product_ids, context=context)

        for product in products:
            if add_qty > product.qty_available:
                return False

        return True

    @http.route(
        ['/shop',
         '/shop/page/<int:page>',
         '/shop/category/<model("product.public.category"):category>',
         '/shop/category/<model("product.public.category"):category>/page/<int:page>'],
        type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        cr = request.cr
        uid = request.uid
        context = request.context
        pool = request.registry

        domain = request.website.sale_product_domain()
        if search:
            for srch in search.split(" "):
                domain.append(('name', 'ilike', srch))

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        keep = QueryURL(
            '/shop', category=category and int(category),
            search=search, attrib=attrib_list)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(
                cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"
        product_count = product_obj.search_count(
            cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(
                cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=PPG,
            scope=7, url_args=post)
        product_ids = product_obj.search(
            cr, uid, domain, limit=PPG, offset=pager['offset'],
            order='website_published desc, website_sequence desc',
            context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_obj = pool['product.public.category']
        category_ids = category_obj.search(
            cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(
            cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(
            cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(
            cr, uid, from_currency, to_currency, price, context=context)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute().process(products),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [
                s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode(
                [('attrib', i) for i in attribs]),
        }
        return request.website.render("website_sale.products", values)
