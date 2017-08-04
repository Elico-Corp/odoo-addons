# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class product_template(orm.Model):
    _inherit = 'product.template'
    _columns = {
        'name': fields.char(
            'Name', size=128,
            required=True, translate=True,
            select=True),
    }


class product_product(orm.Model):
    _inherit = 'product.product'

    def _alt_language(self, cr, uid, ids, name, args, context=None):
        res = {}
        # TODO not sure the language of en_EN?? exist?
        if_has_alt = self._if_has_alt_lang(cr, uid, context=context)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = if_has_alt
        return res

    def _if_has_alt_lang(self, cr, uid, context=None):
        user_obj = self.pool.get('res.users')
        user_rec = user_obj.browse(cr, uid, uid, context=context)
        if user_rec.company_id:
            #TODO here we don't include English as alternate language.
            #  Alex Duan 2014-7-29
            return user_rec.company_id.alt_language not in (
                'en_US', False, None) and user_rec.company_id.alt_language
        return False

    def _get_alt_language(self, cr, uid, ids, name, args, context=None):
        res = {}
        alt_language = self._if_has_alt_lang(cr, uid, context=context)
        ctx = context.copy()
        if alt_language:
            ctx['lang'] = alt_language
            for product in self.browse(cr, uid, ids, context=ctx):
                # alternate solution. Alex
                translated_value = product.name

                # should not use translate api. abandoned.
                origin_name = self.browse(
                    cr, uid, product.id, context=context).name
                res[product.id] = (translated_value != origin_name) and \
                    translated_value or False
        return res

    def get_bilingual_name(self, cr, uid, ids, context={}):
        '''we use this in our report
                suppose len(ids) is only 1.'''
        if not ids:
                return ''
        assert len(ids) == 1, "Suppose to have less then 2 products at a time."
        context['lang'] = 'en_US'
        res = self.name_get(cr, uid, ids, context=context)
        return res and res[0][1] or ''

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not context:
            context = {}
        old_res = super(product_product, self).name_get(
            cr, uid, ids, context=context)
        alt_language = self._if_has_alt_lang(cr, uid, context=context)
        ctx = context.copy()
        if alt_language:
            ctx['lang'] = alt_language
            for r in old_res:
                name = self.read(cr, uid, [r[0]], ['name'])[0].get('name')
                if r:
                    translated_value = self.browse(
                        cr, uid, r[0], context=ctx).name
                    if translated_value and translated_value != name:
                        res.append(
                            (r[0], (r[1] + ' - ' + translated_value)))
                    else:
                        res.append((r[0], r[1]))
        return res or old_res

    def name_search(
            self, cr,
            user, name,
            args=None, operator='ilike',
            context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        name_en = []
        old_ids = super(product_product, self).name_search(
            cr, user, name, args=args, operator=operator,
            context=context, limit=limit)
        for i in old_ids:
            ids.append(i and i[0])
        alt_language = self._if_has_alt_lang(cr, user, context=context)
        if alt_language and name:
            #FIXME for search chinese name, encoding problem. Alex
            sql = (
                "select src from ir_translation " +
                "where lang='%(alt_language)s'" +
                "and value ilike '%(name)s' and name = '%(model_name)s' " +
                "and type = 'model' limit %(limit)d") % \
                {'alt_language': alt_language,
                    'name': name, 'model_name': 'product.template,name',
                    'limit': 10}
            cr.execute(sql)
            english_values = cr.fetchall()
            for english_value in english_values:
                name_en.append(english_value and english_value[0])
        for n in name_en:
            ids.extend(self.search(
                cr, user, [('name', 'ilike', n)] + args,
                limit=limit, context=context))
            ids = list(set(ids))
        return self.name_get(cr, user, ids, context=context)

    _columns = {
        'has_alt_lang': fields.function(
            _alt_language,
            type='boolean',
            store=False,
            string='If Has Alt Language'),
        'alt_name': fields.function(
            _get_alt_language,
            type='char',
            string='Alt Name',
            store=False),
    }
