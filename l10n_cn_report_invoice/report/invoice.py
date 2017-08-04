# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            LIN Yu <lin.yu@elico-corp.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
from lxml import etree
from openerp.osv import osv, fields
from tools.translate import _


class invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            # 'get_partner_ref': self.get_partner_ref,
            'tag': self.tag,
            'get_product_code': self._get_product_code,
            'multiply': self._multiply,
            'get_product_desc': self.get_product_desc,
            'get_product_desc_en': self.get_product_desc_en,
            'get_product_unit': self.get_product_unit,
        })

    # def get_partner_ref(self, partner, product):
    #     result = ''
    #     ref_obj = self.pool.get('product.partner.related.fields')
    #     ref_obj_ids = ref_obj.search(
                            # self.cr, self.uid [('partner_id', '=', partner),
                            # ('product_id', '=', product)])
    #     for ref_obj_id in ref_obj.browse(self.cr, self.uid, ref_obj_ids):
    #         result = ref_obj_id.name + " " + ref_obj_id.value
    #     return result

    def _get_product_code(self, product_id, partner_id):
        product_obj = pooler.get_pool(self.cr.dbname).get('product.product')
        return product_obj._product_code(self.cr, self.uid, [product_id], name=None, arg=None, context={'partner_id': partner_id})[product_id]

    def _multiply(self, one, two):
        return one * two

    def get_product_desc(self, product_id):
        # get desc cn for name, default_cdde, uom
        trans_obj = self.pool.get('ir.translation')
        #name
        trans_ids = trans_obj.search(self.cr, self.uid, [('name','=','product.template,name'),('res_id','=',product_id.id)])
        if trans_ids and trans_ids[0]:
            desc = trans_obj.read(self.cr, self.uid, trans_ids,['value'])[0]['value']
        else:
            desc = u'无'

        # #desc
        # trans_ids = trans_obj.search(self.cr, self.uid, [('field','=','product.template,description'),('res_id','=',product_id.id)])
        # if trans_ids and trans_ids[0]:
        #     desc += trans_obj.read(self.cr, self.uid, trans_ids,['value'])[0]['value']

        if product_id.default_code:
            desc = '[' + product_id.default_code + ']' + ' ' + desc

        #uom
        # trans_ids = trans_obj.search(self.cr, self.uid, [('name','=','product.uom,name'),('res_id','=',product_id.uom_id.id)])
        # if trans_ids and trans_ids[0]:
        #     desc += ' ' + '(' + trans_obj.read(self.cr, self.uid, trans_ids,['value'])[0]['value'] + ')'
        # if product_id.uom_id and product_id.uom_id.name:
        #     desc = desc + ' ' + '(' + product_id.uom_id.name + ')'
        return desc

    def get_product_desc_en(self, product_id):
        desc = product_id.name or ''
        # if product_id.uom_id and product_id.uom_id.name:
        #     desc = desc + ' ' + '(' + product_id.uom_id.name + ')'
        return desc

    def get_product_unit(self, uos_id):
        trans_obj = self.pool.get('ir.translation')
        print uos_id
        print uos_id.name
        desc = uos_id.name
        trans_ids = trans_obj.search(self.cr, self.uid, [('name','=','product.uom,name'),('res_id','=',uos_id.id)])
        if trans_ids and trans_ids[0]:
            desc +=  '/' + trans_obj.read(self.cr, self.uid, trans_ids,['value'])[0]['value']
        # desc = product_id.joomla_unit or ''
        # if product_id.joomla_unit_cn:
        #     desc = desc + ' / ' + product_id.joomla_unit_cn
        return desc

report_sxw.report_sxw(
    'report.invoice.elico', 'account.invoice',
    'addons/elico_bilingual_reports/report/elico_invoice.rml',
    parser=invoice)
