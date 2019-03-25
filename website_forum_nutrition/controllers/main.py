# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import werkzeug.wrappers

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import QueryURL


class Symptom(http.Controller):

    def _get_notifications(self):
        cr, uid, context = request.cr, request.uid, request.context
        Message = request.registry['mail.message']
        badge_st_id = request.registry['ir.model.data'].xmlid_to_res_id(
            cr, uid, 'gamification.mt_badge_granted')
        if badge_st_id:
            msg_ids = Message.search(
                cr, uid,
                [('subtype_id', '=', badge_st_id), ('to_read', '=', True)],
                context=context)
            msg = Message.browse(cr, uid, msg_ids, context=context)
        else:
            msg = list()
        return msg

    def _prepare_forum_values(self, forum=None, **kwargs):
        user = request.registry['res.users'].browse(
            request.cr, request.uid, request.uid, context=request.context)
        values = {
            'user': user,
            'is_public_user': user.id == request.website.user_id.id,
            'notifications': self._get_notifications(),
            'header': kwargs.get('header', dict()),
            'searches': kwargs.get('searches', dict()),
            'validation_email_sent': request.session.get(
                'validation_email_sent', False),
            'validation_email_done': request.session.get(
                'validation_email_done', False),
        }
        values['header']['ask_hide'] = True
        if forum:
            values['forum'] = forum
        elif kwargs.get('forum_id'):
            values['forum'] = \
                request.registry['forum.forum'].browse(
                    request.cr, request.uid,
                    kwargs.pop('forum_id'),
                    context=request.context
            )
        values.update(kwargs)
        return values

    @http.route(
        ['/forum/symptom/<int:symptom_id>/avatar'],
        type='http', auth="public", website=True)
    def symptom_avatar(self, symptom_id=0, **post):
        cr, context = request.cr, request.context
        response = werkzeug.wrappers.Response()
        symptom_obj = request.registry['product.symptom']
        website_obj = request.registry['website']
        symptom = symptom_obj.browse(
            cr, SUPERUSER_ID, symptom_id, context=context)
        if not symptom.exists():
            return website_obj._image_placeholder(response)
        return website_obj._image(
            cr, SUPERUSER_ID, 'product.symptom', symptom.id, 'image', response)

    @http.route(
        ['/forum/<model("forum.forum"):forum>/symptom',
        '/forum/<model("forum.forum"):forum>/symptom/page/<int:page>'],
        type='http', auth="public", website=True)
    def symptom(self, forum, page=1, **searches):
        cr, context = request.cr, request.context
        symptom_obj = request.registry['product.symptom']

        step = 12
        symptom_count = symptom_obj.search(
            cr, SUPERUSER_ID, [], count=True, context=context)
        pager = request.website.pager(
            url="/forum/%s/symptom" % slug(forum), total=symptom_count,
            page=page, step=step, scope=12)

        symptom_ids = symptom_obj.search(
            cr, SUPERUSER_ID, [], limit=step,
            offset=pager['offset'], order='name DESC', context=context)

        # put the symptoms in block of 3 to display them as a table
        symptoms = [[] for i in range(len(symptom_ids) / 4 + 1)]
        for index, sym in enumerate(symptom_obj.browse(
                cr, SUPERUSER_ID, symptom_ids, context=context)):
            symptoms[index / 4].append(sym)
        values = self._prepare_forum_values(forum=forum, searches=searches)
        values .update({
            'symptoms': symptoms,
            'main_object': forum,
            'forum': forum,
            'searches': {'symptom': True},
            'notifications': self._get_notifications(),
            'pager': pager,
        })

        return request.website.render(
            "website_forum_nutrition.symptoms", values)

    @http.route(['/<model("forum.forum"):forum>',
                 '/<model("product.symptom"):symptom>/products',
                 '/<model("forum.forum"):forum>',
                 '/<model("product.symptom"):symptom>',
                 '/products/page/<int:page>',
                 ], type='http', auth="public", website=True)
    def product(self, page=0, symptom=None, forum=None, search='', **post):
        cr, context = request.cr, request.context
        product_obj = request.registry['product.template']
        domain = []
        if symptom:
            domain = [('symptom_ids', 'in', int(symptom.id))]

        step = 12
        product_count = product_obj.search(
            cr, SUPERUSER_ID, domain, count=True, context=context)
        # preparing for the paging.
        pager = request.website.pager(
            url="/%s/%s/products" % (
                slug(forum), slug(symptom)), total=product_count,
            page=page, step=step, scope=12)

        product_ids = product_obj.search(
            cr, SUPERUSER_ID, domain, limit=step,
            offset=pager['offset'],
            order='website_published desc, website_sequence desc',
            context=context)

        # put the symptoms in block of 3 to display them as a table
        products = [[] for i in range(len(product_ids) / 3 + 1)]
        for index, sym in enumerate(product_obj.browse(
                cr, SUPERUSER_ID, product_ids, context=context)):
            products[index / 3].append(sym)
        # searches['symptom'] = 'True'

        # preparing the history bar
        url = '/forum/%s/symptom' % slug(forum)
        keep = QueryURL(url)

        values = self._prepare_forum_values(forum=forum, searches=post)
        values.update({
            'products': products,
            'main_object': forum,
            'keep': keep,
            'forum': forum,
            'searches': {'symptom': True},
            'notifications': self._get_notifications(),
            'pager': pager,
        })

        return request.website.render(
            "website_forum_nutrition.products", values)
