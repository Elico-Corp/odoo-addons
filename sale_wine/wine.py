# -*-coding:utf-8-*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields
from tools.translate import _


class wine_grape(orm.Model):
    _name = "wine.grape"
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
