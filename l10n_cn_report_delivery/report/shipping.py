# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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
import pooler
from osv import osv,fields
from tools.translate import _

class shipping(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(shipping, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_add_header':self._add_header,
            'get_partner_ref':self.get_partner_ref,
            'tag':self.tag
        })
        
    def get_partner_ref(self, partner, product):
        result =''
#        ref_obj=self.pool.get('product.partner.related.fields')
#        ref_obj_ids=ref_obj.search(self.cr, self.uid, [('partner_id', '=', partner),('product_id', '=',product)])
#        for ref_obj_id in ref_obj.browse(self.cr, self.uid, ref_obj_ids):
#            result= ref_obj_id.name + " " + ref_obj_id.value
        return result
    
    def _add_header(self, rml_dom, header='external'):
        if header=='internal':
            rml_head =  self.rml_header2
        elif header=='internal landscape':
            rml_head =  self.rml_header3
        elif header=='external':
            rml_head =  self.rml_header
        else:
            header_obj= self.pool.get('res.header')
            rml_head_id = header_obj.search(self.cr,self.uid,[('name','=',header)])
            if rml_head_id:
                rml_head = header_obj.browse(self.cr, self.uid, rml_head_id[0]).rml_header
        try:
            head_dom = etree.XML(rml_head)
        except:
            raise osv.except_osv(_('Error in report header''s name !'), _('No proper report''s header defined for the selected report. Check that the report header defined in your report rml_parse line exist in Administration/reporting/Reporting headers.' ))
            
        for tag in head_dom:
            found = rml_dom.find('.//'+tag.tag)
            if found is not None and len(found):
                if tag.get('position'):
                    found.append(tag)
                else :
                    found.getparent().replace(found,tag)
        return True

report_sxw.report_sxw('report.l10n.cn.shipping', 'stock.picking', 'addons/l10n_cn_report_delivery/report/shipping.rml', parser=shipping, header="external landscape")

