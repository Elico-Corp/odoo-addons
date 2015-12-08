# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################

from openerp.report import report_sxw

class safety_certificate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(safety_certificate, self).__init__(cr, uid, name, context=context)  
        self.localcontext.update({'get_details': self.get_details}) 
        self.context = context
        
    def get_details(self, start_date, end_date):
        certificate_obj = self.pool.get("property.safety.certificate")
        certificate_ids = certificate_obj.search(self.cr, self.uid, [('expiry_date','>=',start_date),('expiry_date','<=',end_date)])
        certificate_rec = certificate_obj.browse(self.cr, self.uid, certificate_ids)
        return certificate_rec

report_sxw.report_sxw('report.safety.certificate.expiry', 'account.asset.asset',
        'addons/property_management/report/safety_certificate.rml', parser=safety_certificate)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: