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

import datetime
from openerp.report import report_sxw

class pending_rent(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(pending_rent, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'test_date' : self.check_date, 'time':datetime.date.today().strftime('%d-%m-%Y')})
        self.context=context
        
    def check_date(self, start_date):
        if start_date > datetime.date.today().strftime('%Y-%m-%d'):
            return True
        else:
            return False
          
    
report_sxw.report_sxw('report.report.pending.rent', 'tenancy.rent.schedule',
        'addons/property_management/report/pending_rent.rml', parser=pending_rent)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
