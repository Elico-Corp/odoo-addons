# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv, fields

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def print_delivery_note(self, cr, uid, ids, context=None):
        '''
        This function prints the delivery note
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        datas = {
                 'model': 'stock.picking',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
                 'is_default_lang': self._is_default_lang
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'print.delivery.note', 'datas': datas, 'nodestroy': True}

    def _is_default_lang(self, user, partner_lang):
        # TODO not sure if all Odoo's default language is en_US
        '''decide if we print the alt_name of product.
            * first check if we have alt_language defined in user's company.
            * check if the partner's language is default: en_US'''
        if user.company_id and user.company_id.alt_language:
            return user.company_id.alt_language in ('en_US', None, False)
        elif partner_lang:
            return (partner_lang in ('en_US', None, False))
        else:
            return True
stock_picking()

