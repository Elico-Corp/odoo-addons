    # -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, orm


class res_intercompany(orm.Model):
    _inherit = 'res.intercompany'

    def _select_concepts(self, cr, uid, context=None):
        """ Available concepts

        Can be inherited to add custom versions.
        """
        res = super(res_intercompany, self)._select_concepts(cr, uid, context)
        res += [('so2po', 'SO to PO'),
                ('so2so', 'SO to SO'),
                ('po2so', 'PO to SO')]
        return res

    def _select_models(self, cr, uid, context=None):
        """ Available Object names

        Can be inherited to add custom versions.
        """
        res = super(res_intercompany, self)._select_models(
            cr, uid, context)
        new_dict = {'so2po': 'sale.order',
                    'so2so': 'sale.order',
                    'po2so': 'purchase.order'}
        res = dict(res.items() + new_dict.items())
        return res

    _columns = {
        'concept': fields.selection(_select_concepts, string="Concept",
                                    required=True),
    }
