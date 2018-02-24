# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models ,api ,fields
from odoo.exceptions import UserError
from datetime import datetime
import datetime as dt

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    @api.constrains('number_of_days_temp')
    def leave_request_date_constrains(self):
        for record in self:
            if record.number_of_days_temp > 1 and record.number_of_days_temp % 1 != 0:
                raise UserError(
                    'The date you leave that more than one day should be Integer.\
                    For example, if you leave 2.5 days, you should request twice \
                    with 2 days and 0.5 day')

    @api.multi
    def action_approve(self):
        super(HrHolidays, self).action_approve()
        account_analytic_line = self.env['account.analytic.line']
        account_obj = self.env.user.company_id.account_id
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.uid)]).id
        if not account_obj:
            raise UserError(
                'There is no account_id link to leave request.\
                Please config it in setting/Users/companies')
        project_obj = self.env['project.project'].search([
                            ('analytic_account_id', '=', account_obj.id)])
        if not project_obj:
            raise UserError(
                'lack a project_id, need set it related with an account_id which \
                config in setting/Users/companies')
        for record in self:
            date = record.date_from.split(' ')[0]
            if record.number_of_days_temp < 1:
                display_name = '%s on %s: %s day' %(record.env.user.name, \
                    account_obj.name, record.number_of_days_temp)
                vals = {
                    'name':record.name or display_name,
                    'account_id':account_obj.id,
                    'date':date,
                    'amount':0,
                    'unit_amount':record.number_of_days_temp*8,
                    'project_id':self.env['project.project'].search([
                        ('analytic_account_id', '=', account_obj.id)]).id,
                    'sheet_id':self._get_sheet_id(employee_id, date), 
                    'user_id':record.env.user.id,
                    'employee_id':employee_id,
                }
                account_analytic_line.create(vals)
            else:
                for i in range(int(record.number_of_days_temp)):
                    date = self.date_add_one_day(date)
                    display_name = '%s on %s: one day' %(record.env.user.name, \
                    account_obj.name)
                    vals = {
                        'name':record.name or display_name,
                        'account_id':account_obj.id,
                        'date':date,
                        'amount':0,
                        'unit_amount':8,
                        'project_id':self.env['project.project'].search([
                            ('analytic_account_id', '=', account_obj.id)]).id,
                        'sheet_id':self._get_sheet_id(employee_id, date), 
                        'user_id':record.env.user.id,
                        'employee_id':employee_id,
                    }
                    account_analytic_line.create(vals)
        return True

    def _get_sheet_id(self, employee_id, date):
        """ this method will always return a sheet_id, if leave request's date 
        is not in current timesheet, just create a timesheet with leave request
        date's week
        """
        sheet_id=self.env['hr_timesheet_sheet.sheet'].search([
            ('employee_id', '=', employee_id), 
            ('date_from', '<=', date), 
            ('date_to', '>=', date)]).id
        if sheet_id:
            return sheet_id
        else:
            date_obj=datetime.strptime(date, '%Y-%m-%d')
            date_from_obj=date_obj+dt.timedelta(days=-date_obj.weekday())
            date_from = date_from_obj.strftime('%Y-%m-%d')
            date_to=(date_from_obj+dt.timedelta(days=7)).strftime('%Y-%m-%d')
            vals={
                'employee_id':employee_id, 
                'date_from':date_from, 
                'date_to':date_to ,
            }
            return self.env['hr_timesheet_sheet.sheet'].create(vals).id

    def date_add_one_day(self, date):
        date_obj=datetime.strptime(date, '%Y-%m-%d')
        date_add=date_obj+dt.timedelta(days=1)
        return date_add.strftime('%Y-%m-%d')