# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
from tools.translate import _
import re

class product_stock_type(osv.osv):
    _name = "product.stock_type"
    _columns = {
        'name': fields.char('Name', size=32, translate=True),
        'code': fields.char('Code', size=12),
        #'location_ids': fields.one2many('stock.location', 'stock_type_id', _('Location for this stock type')),
    }
product_stock_type()


class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'stock_type_id': fields.many2one('product.stock_type', 'Stock Type', change_default=True),
        'name': fields.char('Name', size=128, translate=True, select=True),
        #'ul_id': fields.many2one('product.ul','Packaging'),
    }
product_template()


class product_product(osv.osv):
    _inherit = "product.product"

    def _name_en(self, cursor, uid, ids, fields, arg, context=None, maxlength=2048):
        result = {}
        for product in self.browse(cursor, uid, ids, context=context):
            cursor.execute("SELECT name_template FROM product_product WHERE id = %s" % (product.id))
            name = cursor.fetchone()
            result[product.id] = name[0]
            # cursor.execute("SELECT name, name_template FROM product_product WHERE id = %s" % (product.id))
            # name = cursor.fetchone()
            # if name and name[0]:
            #     result[product.id] = name[0]
            # elif name and name[1]:
            #     result[product.id] = name[1]
        return result


    def _name_cn(self, cursor, uid, ids, fields, arg, context=None, maxlength=2048):
        result = {}
        for product in self.browse(cursor, uid, ids, context=context):
            cursor.execute("SELECT name_template FROM product_product WHERE id = %s" % product.id)
            t_name = cursor.fetchone()
            t_ids = False
            if t_name and t_name[0]:
                value = re.sub("'", "''", t_name[0])

                cursor.execute("SELECT value FROM ir_translation WHERE lang = 'zh_CN' " + \
                 " AND name ='product.product,name' AND src = '%s' AND type = 'model' AND res_id = %s" % (value, product.id))
                t_ids = cursor.fetchone()
            if not t_ids:
                cursor.execute("SELECT value FROM ir_translation WHERE lang = 'zh_CN' " + \
                 " AND name ='product.product,name' AND type = 'model' AND res_id = %s" % (product.id))
                t_ids = cursor.fetchone()
            if t_ids:
                result[product.id] = t_ids[0]
        return result


    def _name_sort_en(self, cursor, uid, ids, fields, arg, context=None, maxlength=2048):
        result = {}
        for product in self.browse(cursor, uid, ids, context=context):
            result[product.id] = product.name_en
        return result
    
    def _name_sort_cn(self, cursor, uid, ids, fields, arg, context=None, maxlength=2048):
        result = {}
        for product in self.browse(cursor, uid, ids, context=context):
            result[product.id] = product.name_cn
        return result
    

    def _name_en_inv(self, cursor, user, id, name, value, arg, context=None):
        """ All the logic is in the onchange_name_en()
            Need to update the Translation table directly
            If default language is English, then only need to save the name (useless)
            If default language is Chinese, then we need to update the propduct_product table directly
        """
        if value:
            value = re.sub("'", "''", str(value.encode('utf-8')))
            cursor.execute("UPDATE product_template SET name = '%s' WHERE id = %s" % (value, id))


    def onchange_name_en(self, cursor, uid, ids, name_en):
        result = {}
        if name_en:
            # only do that in English
            obj = self.pool.get('res.users').browse(cursor, uid, uid)
            if obj.lang == 'en_US':
                result['name'] = name_en
        return result and {'value': result}


    def _name_cn_inv(self, cursor, user, id, name, value, arg, context=None):
        if value:
            tr_pool = self.pool.get('ir.translation')
            for product in self.browse(cursor, user, [id], context=context):
                cursor.execute("SELECT name_template FROM product_product WHERE id = %s" % id)
                t_name = cursor.fetchone()
                t_ids = False
                
                # Do we have a source: 'src'
                if t_name[0]:
                    t_ids = tr_pool.search(cursor, user,
                                     [('lang', '=', 'zh_CN'), ('name', '=', 'product.product,name'),
                                      ('type', '=', 'model'), ('src', '=', t_name[0]), ('res_id', '=', id)])
                
                # It did not work with a source, lets try without a source
                if not t_ids:
                    t_ids = tr_pool.search(cursor, user,
                                     [('lang', '=', 'zh_CN'), ('name', '=', 'product.product,name'),
                                      ('type', '=', 'model'), ('res_id', '=', id)])

                # Did we find something, with or without a source
                if t_ids:
                    tr_pool.write(cursor, user, t_ids, {'value': value})
                else:
                    vals = {
                       'lang': 'zh_CN',
                       'name': 'product.product,name',
                       'type': 'model',
                       'value': value,
                       'res_id':id,
                    }
                    if t_name[0]:
                        vals['src'] = t_name[0]
                    tr_pool.create(cursor, user, vals)


    _columns = {
        'packing_sequence': fields.integer('Packing Sequence'),
        'deliver_in':fields.selection([('normal',_('normal')),('iced',_('Iced')),('warm',_('Warm')),('cold',_('Cold')),('iced_n_warm',_('Warm & Cold'))],_('Website Product Deliver In'),help="Website Product Deliver In", size=128, required=True),
        'name_en':          fields.function(_name_en, method=True, type='char', size=128, string=_('Name EN'), fnct_inv=_name_en_inv),
        'name_cn':          fields.function(_name_cn, method=True, type='char', size=128, string=_('Name CN'), fnct_inv=_name_cn_inv),
        'name_sort_en':     fields.function(_name_sort_en, method=True, type='char', size=128, store={'product.product': (lambda self, cr, uid, ids, c={}: ids, ['name_en'], 10)}, string=_('Name EN')),
        'name_sort_cn':     fields.function(_name_sort_cn, method=True, type='char', size=128, store={'product.product': (lambda self, cr, uid, ids, c={}: ids, ['name_cn'], 10)}, string=_('Name CN')),
    }

    _defaults = {
       'deliver_in': 'normal',
    }
product_product()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    def _move_to_update_folowing_product_packing_sequence_change(self, cr, uid, ids, fields=None, arg=None, context=None):
        if type(ids) != type([]):
            ids = [ids]
        return self.pool.get('stock.move').search(cr, uid, [('product_id', 'in', ids)]) or []
    
    def _get_packing_sequence(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
           if move.product_id:
               result[move.id] = int(move.product_id.packing_sequence)
           else:
               result[move.id] = 0
        return result    
    
    _store_packing_sequence = {
        'stock.move': (lambda self, cr, uid, ids, context: ids, ['product_id'], 10),
        'product.product': (_move_to_update_folowing_product_packing_sequence_change, ['packing_sequence'], 10)
    }
    
    _columns = {
        'packing_sequence': fields.function(_get_packing_sequence, method=True, type='integer', store=_store_packing_sequence, string='Packing Sequence'),
    }
stock_move()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
