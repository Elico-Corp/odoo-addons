# -*-coding:utf-8-*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields

WINE_TYPE_EN_MAPPING = {
    'red_wine': 'Red wine',
    'white_wine': 'White wine',
    'rose_wine': 'Rosé wine',
    'sweet_wine': 'Sweet wine',
    'champagne': 'Champagne',
    'sparkling_wine': 'Sparkling wine',
}


class product_product(orm.Model):
    _inherit = "product.product"

    _columns = {
        'name_cn': fields.char(string="Name CN", translate=True),
        'wine_type': fields.selection(
            WINE_TYPE_EN_MAPPING.items(),
            'Wine Type'),
        'producer_id': fields.many2one('wine.producer', 'Producer'),
        'country_id': fields.many2one('res.country', string="Country"),
        'state_id': fields.many2one('res.country.state', string="Region"),
        'capacity_id': fields.many2one('product.uom', string="Capacity"),
        'grape_id': fields.many2one('wine.grape', string="Main Grape"),
    }

    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)',
            'This Internal Reference (SKU) is already used!'),
    ]

    def onchange_country_id(self, cr, uid, ids, country_id, context=None):
        d = {}
        if country_id:
            d = {'state_id': [('country_id', '=', country_id)]}
        return {'domain': d}

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}

        default.update(
            {'default_code': False,
             # to fix error dupllicating a product
             # while it duplicate attribute set, it may have error
             'attribute_set_id': False,
             })
        return super(product_product, self).copy(
            cr, uid, id, default, context=context)


class res_country_state(orm.Model):
    _inherit = "res.country.state"

    _columns = {
        'code': fields.char(string="State Code", size=3, invisible="True"),
        'name': fields.char(string="State Name", translate=True)
    }


class product_template(orm.Model):
    _inherit = "product.template"

    _columns = {
        'name': fields.char('Name', size=128, translate=False,
                            select=True, required = True),
    }

class wine_producer(orm.Model):
    _name = "wine.producer"
    _rec_name = "name_en"

    _columns = {
        'name_en': fields.char(string="Name EN", required=True),
        'name_cn': fields.char(string="Name CN"),
    }

    _sql_constraints = [
        ('name_en_uniq', 'unique (name_en)',
         'The English name of the field has to be unique !'),
        ('name_cn_uniq', 'unique (name_cn)',
         'The chinese name of the field has to be unique !'),
    ]

    def name_get(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').read(
            cr, uid, uid, ['lang'], context)
        self._rec_name = 'name_en'
        if user['lang'] == "zh_CN":
            self._rec_name = 'name_cn'
        res = [(r['id'], r[self._rec_name])
               for r in self.read(cr, uid, ids, [self._rec_name], context)]
        return res
