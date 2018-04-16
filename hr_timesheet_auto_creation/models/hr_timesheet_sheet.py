# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models

from datetime import datetime, timedelta


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.model
    def create_employee_timesheet(self):
        employee_obj = self.env['hr.employee']
        employee_ids = employee_obj.search([('active', '=', True),
                                            ('user_id', '!=', False),
                                            ]).ids
        today = datetime.now()
        monday = today + timedelta(days=-today.weekday())
        sunday = monday + timedelta(days=+6)
        # Search for existing timesheet
        exists_timesheet_records = self.search([('date_to', '>=', monday)])
        ignore_employee_ids = map(lambda x: x.employee_id.id,
                                  exists_timesheet_records)
        employee_ids = list(set(employee_ids) - set(ignore_employee_ids))
        vals = {
            'date_from': monday.strftime('%Y-%m-%d'),
            'date_to': sunday.strftime('%Y-%m-%d')
        }
        for employee_id in employee_ids:
            vals['employee_id'] = employee_id
            self.sudo().create(vals)
        return True
