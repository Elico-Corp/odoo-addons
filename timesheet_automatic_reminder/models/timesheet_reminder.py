# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (http://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from collections import defaultdict
from openerp import models, api, fields
from openerp.tools import DEFAULT_SERVER_TIME_FORMAT as TIME_FORMAT, \
    DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class RemindDateLine(models.TransientModel):
    _name = 'reminder.date.line'
    _description = 'Date need reminder lines'

    reminder_date = fields.Date('Reminder Date')
    leave_hours = fields.Float('Leave Hours')
    work_hours = fields.Float('Work Hours')
    lack_hours = fields.Float('Lack Hours')
    reminder_id = fields.Many2one(
        'timesheet.reminder',
        'Reminder Timesheet',
        ondelete='cascade'
    )


class TimesheetReminder(models.TransientModel):
    _name = 'timesheet.reminder'
    _description = 'TimeSheet Reminder'
    _inherit = ['mail.thread']

    employee_id = fields.Many2one('hr.employee', 'Employee')
    manager_id = fields.Many2one(
        'hr.employee',
        'Employee Manager',
        related='employee_id.parent_id',
        store=True
    )
    reminder_date_ids = fields.One2many(
        'reminder.date.line',
        'reminder_id',
        string='Reminder Date'
    )

    @staticmethod
    def _get_leave_to_days(leave, work_start, work_end, employee_leave_dict):
        """
        Distinguish the vacation days to separate dates
        :param leave: need distinguished leave record
        :param period_date: need sorted days
        :param employee_leave_dict: result
        :return: employee_leave_dict
        """
        employee = leave.employee_id
        _start_leave = fields.Datetime.from_string(leave.date_from)
        start_leave = fields.Datetime.context_timestamp(employee, _start_leave)
        _end_leave = fields.Datetime.from_string(leave.date_to)
        end_leave = fields.Datetime.context_timestamp(employee, _end_leave)
        diff_days = (end_leave - start_leave).days
        count = 0
        check_date = start_leave.date()
        start_leave_date = start_leave.date()
        end_leave_date = end_leave.date()
        one_day = timedelta(days=1)
        while count <= diff_days:
            if check_date.strftime(DATE_FORMAT) in employee_leave_dict[employee.id]:
                if start_leave_date == check_date and end_leave_date == check_date:
                    _sl, _el = start_leave, end_leave
                elif start_leave_date == check_date and end_leave_date != check_date:
                    _sl = start_leave
                    _el = datetime.combine(check_date,
                                           datetime.strptime('23:59:59', TIME_FORMAT).time())\
                        .replace(tzinfo=start_leave.tzinfo)
                elif start_leave_date != check_date and end_leave_date == check_date:
                    _el = end_leave
                    _sl = datetime.combine(check_date,
                                           datetime.strptime('00:00:00', TIME_FORMAT).time())\
                        .replace(tzinfo=end_leave.tzinfo)
                else:
                    employee_leave_dict[employee.id][check_date.strftime(DATE_FORMAT)] += 9
                    count += 1
                    check_date += one_day
                    continue
                work_on = datetime.combine(check_date, work_start).replace(tzinfo=_sl.tzinfo)
                work_off = datetime.combine(check_date, work_end).replace(tzinfo=_el.tzinfo)
                leave_on = _sl if _sl > work_on else work_on
                leave_off = _el if _el < work_off else work_off
                leave_hours = leave_off.hour - leave_on.hour
                employee_leave_dict[employee.id][check_date.strftime(DATE_FORMAT)] += \
                    leave_hours if leave_hours > 0 else 0
            count += 1
            check_date += one_day
        return employee_leave_dict

    @api.model
    def _get_employee_leaves(self, yesterday, count_days, work_start,
                             work_end, employee_records=None):
        """
        Get the leave time about every employee
        :param start_datetime:
        :param end_datetime:
        :param employee_records:
        :return:
        """
        end_datetime = yesterday.strftime(DATETIME_FORMAT)
        count_date = [yesterday.date()]
        while len(count_date) < count_days:
            s = (count_date[-1] - timedelta(days=1))
            count_date.append(s)
        start_datetime = count_date[-1].strftime(DATETIME_FORMAT)
        holiday_obj = self.env['hr.holidays']
        if not employee_records:
            employee_records = self.env['hr.employee'].search([])
        count_date_str = [r.strftime(DATE_FORMAT) for r in count_date]
        employee_leave_dict = defaultdict(dict)
        for employee in employee_records:
            employee_leave_dict[employee.id] = dict.fromkeys(count_date_str, 0)
        leave_records = holiday_obj.search([
            ('employee_id', 'in', employee_records.ids),
            ('type', '=', 'remove'),
            ('state', 'not in', ['cancel', 'refuse']),
            '|', '&',
            ('date_from', '>=', start_datetime),
            ('date_from', '<=', end_datetime),
            '&',
            ('date_to', '>=', start_datetime),
            ('date_to', '<=', end_datetime)
        ], order='date_from')
        for leave in leave_records:
            employee_leave_dict = self._get_leave_to_days(leave, work_start,
                                                          work_end, employee_leave_dict)
        return employee_leave_dict

    @api.model
    def _get_employee_tms(self, end_date, count_days, employee_records=False):
        """
        Search the time sheet records to find out the employee
        TMS hours during the check period
        :param end_date: The last check date
        :param count_days: the days need to check
        :param employee_records: the employee need check
        :return: (type: dict) {employee_id: {date1: hours, date2: hours, ...}, ...}
        """
        end_date_str = end_date.strftime(DATE_FORMAT)
        start_date = end_date - timedelta(days=count_days)
        start_date_str = start_date.strftime(DATE_FORMAT)
        if not employee_records:
            employee_records = self.env['hr.employee'].search([])

        user_employee_dict = defaultdict(set)
        [user_employee_dict[x.user_id.id].add(x.id) for x in employee_records]

        tms_obj = self.env['hr.analytic.timesheet']
        tms_records = tms_obj.search([
            ('user_id', 'in', user_employee_dict.keys()),
            ('date', '>=', start_date_str),
            ('date', '<=', end_date_str)
        ])
        employee_timesheet_dict = defaultdict(dict)
        for tms in tms_records:
            user_id = tms.user_id.id
            tms_date = tms.date
            for emp_id in user_employee_dict.get(user_id, []):
                if tms.date not in employee_timesheet_dict[emp_id]:
                    employee_timesheet_dict[emp_id][tms_date] = 0
                employee_timesheet_dict[emp_id][tms_date] += tms.unit_amount

        return employee_timesheet_dict

    @api.model
    def _start_remind(self, count_days, workstart, workend,
                      rest_hours, reminder_type=1):
        """
        The cron job start part, find the employee who didn't input his TMS and create the
        record for reminder his manager in the noon
        :param count_days: how many days need check
        :param workstart: the time when you start work(work on)
        :param workend: the time when you end work(work off)
        :param resethours: during the work time how many hours you get to reset
        :param reminder_type: Choose the email send to employee(1) or manager(2)
        :return:
        """
        delta_one_day = timedelta(days=1)
        employee_records = self.env['hr.employee'].search([])
        _yesterday = (datetime.now() - delta_one_day)
        workstart_time = datetime.strptime(workstart, TIME_FORMAT).time()
        workend_time = datetime.strptime(workend, TIME_FORMAT).time()
        employee_leave_dict = self._get_employee_leaves(_yesterday, count_days,
                                                        workstart_time, workend_time,
                                                        employee_records=employee_records)
        employee_tms_dict = self._get_employee_tms(_yesterday, count_days,
                                                   employee_records=employee_records)
        need_work_hours = workend_time.hour - workstart_time.hour - rest_hours
        reminder_records = self.\
            _create_employee_reminder_records(_yesterday, count_days, employee_records,
                                              employee_leave_dict, employee_tms_dict,
                                              need_work_hours)
        if reminder_type == 2:
            self._send_email_reminder_manager(reminder_records=reminder_records)
        else:
            self._send_email_reminder_employee(reminder_records=reminder_records)

        return True

    @api.model
    def _check_is_working_day(self, check_date, employee_id=None):
        """
        Check the date belong to working day or rest day
        :param selected_date: the date need to checked
        :param employee_id: the employee need checked
        :return: if the check_date is working day return True, otherwise return False
        """
        public_holiday_obj = self.env['hr.holidays.public']
        if isinstance(check_date, basestring):
            check_date = fields.Date.from_string(check_date)
        _is_weekend = True if check_date.weekday() in [5, 6] else False
        _is_public_holiday = public_holiday_obj.\
            is_public_holiday(check_date, employee_id=employee_id)

        return not (_is_weekend or _is_public_holiday)

    @api.model
    def _create_employee_reminder_records(self, end_date, count_days, employee_records,
                                          employee_leave_dict, employee_tms_dict,
                                          need_work_hours):
        """
        Create the records which employee need remind to fill the TMS
        :param end_date: the last check day date
        :param count_days: the days need check
        :param employee_records: the employee need check
        :param employee_leave_dict: record the employee's time for leave
        :param employee_tms_dict: record the employee's time for TMS
        :param need_work_hours: the hours the emloyee need record every day.
        :return: the records need send email
        """
        result = self.env['timesheet.reminder']
        self.search([('create_date', '=', fields.Date.today())]).unlink()
        check_date_list = [end_date - timedelta(x) for x in xrange(count_days)]
        for employee in employee_records:
            emp_id = employee.id
            real_check_list = filter(lambda x: self._check_is_working_day(x, emp_id),
                                     check_date_list)
            reminder_date_ids = []
            for check_date in real_check_list:
                check_date_str = check_date.strftime(DATE_FORMAT)
                leave_hours = employee_leave_dict.get(emp_id, {}).get(check_date_str, 0)
                tms_hours = employee_tms_dict.get(emp_id, {}).get(check_date_str, 0)
                effective_hours = leave_hours + tms_hours

                if need_work_hours > effective_hours:
                    lack_hours = need_work_hours - effective_hours
                    reminder_date_ids.append([0, False, {
                        'leave_hours': leave_hours,
                        'work_hours': tms_hours,
                        'lack_hours': lack_hours,
                        'reminder_date': check_date_str
                    }])
            result |= self.create({
                'employee_id': emp_id,
                'reminder_date_ids': reminder_date_ids,
            })
        return result

    @api.model
    def _send_email_reminder_employee(self, reminder_records, force=False):
        """
        Send the reminder email to employee
        :param reminder_records:
        :param force:
        :return:
        """
        email_from = self.env.user.company_id.email
        data = self.env['ir.model.data']
        mail = self.env['mail.mail']
        template_xmlid = 'employee_reminder_email_template'
        template = data.xmlid_to_object(
            'timesheet_automatic_reminder.{}'.format(template_xmlid))
        mail_ids = []
        for reminder in reminder_records:
            emp_work_email = reminder.employee_id.work_email
            if emp_work_email and email_from and (email_from != emp_work_email or force):
                mail_id = template.with_context(dbname=self.env.cr.dbname).send_mail(reminder.id)
                the_mailmess = mail.browse(mail_id).mail_message_id
                the_mailmess.write({'model': None, 'res_id': False})
                mail_ids.append(mail_id)

        if mail_ids:
            res = mail.send(mail_ids)

        return res

    @api.model
    def _send_email_reminder_manager(self, reminder_records, force=False):
        """
        Send the reminder email to manager
        :param reminder_records:
        :param force:
        :return:
        """
        email_from = self.env.user.company_id.email
        data = self.env['ir.model.data']
        mail = self.env['mail.mail']
        template_xmlid = 'manager_reminder_email_template'
        template = data.xmlid_to_object(
            'timesheet_automatic_reminder.{}'.format(template_xmlid))
        mail_ids = []
        # Get the manger and employee mappping
        manager_employee_dict = {}
        for reminder in reminder_records:
            manager = reminder.employee_id.parent_id
            if not manager:
                continue
            key = manager
            if key not in manager_employee_dict:
                manager_employee_dict[key] = {
                    'manager': manager,
                    'employee': {},
                    'res_id': reminder.id
                }
            reminder_date = (', ').join([x.reminder_date for x in reminder.reminder_date_ids])
            emp_key = (reminder.employee_id.id, reminder.employee_id.name)
            manager_employee_dict[key]['employee'][emp_key] = reminder_date

        for manager_record, real_content in manager_employee_dict.items():
            emp_work_email = manager_record.work_email
            res_id = real_content.pop('res_id')
            if emp_work_email and email_from and (emp_work_email != email_from or force):
                mail_id = template.with_context(manager=real_content).\
                    send_mail(res_id)
                the_mailmess = mail.browse(mail_id).mail_message_id
                the_mailmess.write({'model': None, 'res_id': False})
                mail_ids.append(mail_id)

        if mail_ids:
            res = mail.send(mail_ids)

        return res
