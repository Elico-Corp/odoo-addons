# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import time
import pytz
from openerp import fields, models, api, _


class TimesheetReport(models.TransientModel):
    _name = "timesheet.employee.remind"
    _description = "Timesheet Employee Remind Service"
    _inherit = ['mail.thread']

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    WEEKEND = [5, 6]

    @api.model
    def _start_remind(
            self,
            count_days=7,
            workstart='9:00:00',
            workend='18:00:00',
            resethours=1
    ):
        employee_remind_list = {}
        employee_list = self.env['hr.employee'].search([])
        publicholiday = self.env['hr.holidays.public']
        hranalytictmobj = self.env['hr.analytic.timesheet']
        for employee in employee_list:
            count = 0
            selected_date = datetime.date.today()
            date_one_day = datetime.timedelta(days=1)
            employee_remind_list[employee.id] = []
            while count < count_days:
                selected_date = selected_date - date_one_day
                if not publicholiday.is_public_holiday(
                        selected_date,
                        employee.id
                ) \
                        and not self.is_weekend(
                            selected_date
                ):
                    allhours_expected = self._get_all_hour(
                        selected_date,
                        employee.id,
                        workstart,
                        workend,
                        resethours
                    )
                    if not allhours_expected:
                        continue
                    hrworklist = hranalytictmobj.search([
                        ('date',
                         '=',
                         str(selected_date)),
                        ('user_id',
                         '=',
                         employee.user_id.id)
                    ])
                    if hrworklist:
                        workhours_real = 0
                        for hrwork in hrworklist:
                            workhours_real += hrwork.unit_amount
                        allhours_real = workhours_real + resethours
                        if allhours_expected <= allhours_real:
                            pass
                        else:
                            employee_remind_list[employee.id].append(
                                str(selected_date)
                            )
                    else:
                        employee_remind_list[employee.id].append(
                            str(selected_date)
                        )
                    count += 1
        self.send_email_employee(employee_remind_list)

    @api.multi
    def send_email_employee(self, employee_remind_list=False):
        hrtimesheetobj = self.env['hr_timesheet_sheet.sheet']
        hremployeeobj = self.env['hr.employee']
        if employee_remind_list:
            for employee_id, date_list in employee_remind_list.items():
                employee = hremployeeobj.browse(employee_id)
                hrtimesheetlist = hrtimesheetobj.search([
                    (
                        'user_id', '=', employee.user_id.id
                    )], order='date_to DESC', )
                if hrtimesheetlist:
                    for hrtimesheet in hrtimesheetlist:
                        hrtimesheet.message_post(
                            body=_("please input your TM in %s") % date_list
                        )
                        break

    def is_weekend(self, selected_date):
        if selected_date.weekday() not in self.WEEKEND:
            return False
        else:
            return True

    @api.multi
    def _get_all_hour(self, selected_date, employee_id, workstart,
                      workend, resethours):
        no_work = 0
        employee = self.env['hr.employee'].browse(employee_id)
        employee_tz_str = employee.user_id.tz
        if employee_tz_str:
            employee_tz = standard_tz = pytz.timezone(employee_tz_str)
        else:
            employee_tz = standard_tz = pytz.utc
        selected_date_start = self._str_to_datetime(
            str(selected_date) + ' ' + str(workstart), standard_tz)
        selected_date_end = self._str_to_datetime(
            str(selected_date) + ' ' + str(workend), standard_tz)
        workhours = selected_date_end.hour - selected_date_start.hour
        hrholidayobj = self.env['hr.holidays']
        leaves = hrholidayobj.search(
            [
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('state', 'not in', ('cancel', 'refuse'))
            ]
        )
        if not leaves:
            return workhours + resethours
        for leave in leaves:
            leave_date_from = self._tz_offset(
                leave.date_from, employee_tz
            )
            leave_date_to = self._tz_offset(
                leave.date_to, employee_tz
            )
            if leave_date_from >= selected_date_start \
                    and leave_date_from < selected_date_end <= leave_date_to:
                return leave_date_from.hour - selected_date_start.hour
            elif leave_date_from >= selected_date_start \
                    and selected_date_end >= leave_date_to:
                return leave_date_from.hour - selected_date_start.hour + \
                    selected_date_end.hour - leave_date_to.hour
            elif leave_date_to <= selected_date_end \
                    and leave_date_to > selected_date_start >= leave_date_from:
                return selected_date_end.hour - leave_date_to.hour
            elif leave_date_from < selected_date_start \
                    and selected_date_end < leave_date_to:
                return no_work
        return workhours + resethours

    def _str_to_datetime(self, str=False, standard_tz=False):
        return datetime.datetime.strptime(
            time.strftime(str),
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=standard_tz)

    def _tz_offset(self, str=False, employee_tz=False):
        utc_date = datetime.datetime.strptime(
            time.strftime(str),
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=pytz.utc)
        return utc_date.astimezone(employee_tz)
