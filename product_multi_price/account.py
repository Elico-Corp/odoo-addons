# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# © 2014 Akretion Benoît GUILLOT (benoit.guillot@akretion.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv.orm import Model
from openerp.osv import fields

class account_tax(Model):
    _inherit = 'account.tax'
    _columns = {
        'related_inc_tax_id': fields.many2one('account.tax', 'Related Included Tax', domain=[('price_include','=', True)]),
        }

    # overload def compute all but add a choice for the decimal precision
    def compute_all_with_precision(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None, force_excluded=False, precision=None):
        """
        :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
            tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
            False
        RETURN: {
                'total': 0.0,                # Total without taxes
                'total_included: 0.0,        # Total with taxes
                'taxes': []                  # List of taxes, see compute for the format
            }
        """
        if not precision:
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        totalin = totalex = round(price_unit * quantity, precision)
        tin = []
        tex = []
        for tax in taxes:
            if not tax.price_include or force_excluded:
                tex.append(tax)
            else:
                tin.append(tax)
        tin = self.compute_inv(cr, uid, tin, price_unit, quantity, address_id=address_id, product=product, partner=partner)
        for r in tin:
            totalex -= r.get('amount', 0.0)
        totlex_qty = 0.0
        try:
            totlex_qty = totalex/quantity
        except:
            pass
        tex = self._compute(cr, uid, tex, totlex_qty, quantity, address_id=address_id, product=product, partner=partner)
        for r in tex:
            totalin += r.get('amount', 0.0)
        return {
            'total': totalex,
            'total_included': totalin,
            'taxes': tin + tex
            }
