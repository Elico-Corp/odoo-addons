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

class income_expenditure(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(income_expenditure, self).__init__(cr, uid, name, context=context)  
        self.total_in = 0.00
        self.total_ex = 0.00
        self.total_gr = 0.00
        self.localcontext.update({'get_details': self.get_details, 'get_income_total' : self.get_income_total, 'get_expence_total' : self.get_expence_total, 'get_grand_total' : self.get_grand_total}) 
        
        self.context = context
        
    def get_details(self, start_date, end_date):
        property_obj = self.pool.get('account.asset.asset')
        maintenance_obj = self.pool.get("property.maintenance")
        income_obj = self.pool.get("tenancy.rent.schedule")
        property_ids = property_obj.search(self.cr, self.uid, [])
        property_rec = property_obj.browse(self.cr, self.uid, property_ids)
        report_rec = []
        for property_id in property_rec:
            maintenance_ids = maintenance_obj.search(self.cr, self.uid, [('date','>=',start_date),('date','<=',end_date),('property_id','=',property_id.id)])
            tenancy_ids = []
            for tenancy_rec in property_id.tenancy_property_ids:
                tenancy_ids.append(tenancy_rec.id)
            income_ids = income_obj.search(self.cr, self.uid, [('start_date','>=',start_date),('start_date','<=',end_date),('tenancy_id','in',tenancy_ids)])
            maintenance_rec = maintenance_obj.browse(self.cr, self.uid, maintenance_ids)
            income_rec = income_obj.browse(self.cr, self.uid, income_ids)
            total_income = 0
            total_expence = 0
            for income_id in income_rec:
                total_income += income_id.amount
            for expence_id in maintenance_rec:
                
                total_expence += expence_id.cost
            self.total_in += total_income 
            self.total_ex += total_expence
            report_rec.append({'property' : property_id.name, 'total_income' : total_income, 'total_expence' : total_expence})
        self.total_gr = self.total_in - self.total_ex
        
        return report_rec

    def get_income_total(self):
        return self.total_in
    
    def get_expence_total(self):
        return self.total_ex
    
    def get_grand_total(self):
        return self.total_gr

report_sxw.report_sxw('report.income.expenditure', 'account.asset.asset',
        'addons/property_management/report/income_expenditure.rml', parser=income_expenditure)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: