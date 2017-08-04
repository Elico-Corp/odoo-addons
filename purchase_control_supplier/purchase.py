# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields

class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):

        if context and context.get('supplier_id', False):
            product_limit = self.pool.get('res.partner').read(cr,uid,context['supplier_id'],['supplier_product_limit'])['supplier_product_limit']
            if product_limit:
                #    ids = []
                cr.execute("SELECT distinct(product_id) FROM product_supplierinfo where name = %s" % (context.get('supplier_id')))
                ids = [x[0] for x in cr.fetchall()]
                args.append(('id', 'in', ids))
                order = 'default_code'
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

product_product()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    _columns = {
        'supplier_product_limit':fields.boolean("Control Supplier Search", help="""If checked, allows you to search only the product in this supplier )"""),
    }

    _defaults = {
        'supplier_product_limit': True,
    }