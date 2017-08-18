# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from openerp import models, api


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.model
    def create_employee_timesheet(self):
        employee_obj = self.env['hr.employee']
        employee_records = employee_obj.search([('active', '=', True),
                                                ('user_id', '!=', False),
                                                ('product_id', '!=', False),
                                                ('journal_id', '!=', False)
                                                ])
        today = datetime.now()
        monday = (today + timedelta(days=-today.weekday()))
        sunday = monday + timedelta(days=+6)
        exists_timesheet_records = self.search([('date_to', '>=', monday)])
        ignore_employee_ids = map(lambda x: x.employee_id.id,
                                  exists_timesheet_records)
        vals = {
            'date_from': monday.strftime('%Y-%m-%d'),
            'date_to': sunday.strftime('%Y-%m-%d')
        }
        for employee in employee_records:
            if employee.id in ignore_employee_ids:
                continue
            vals['employee_id'] = employee.id
            self.sudo().create(vals)

        return True
