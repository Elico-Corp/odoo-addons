# -*- coding: utf-8 -*-
# © 2017 Elico corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from openerp import models, api, fields
from openerp.tools import DEFAULT_SERVER_TIME_FORMAT as TIME_FORMAT, \
    DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class RemindDateLine(models.TransientModel):
    _name = 'reminder.date.line'
    _description = 'Date need reminder lines'

    reminder_date = fields.Date('Reminder Date')
    leave_hours = fields.Float('Leave Hours', compute='_get_leave_hours')
    work_hours = fields.Float('Work Hours', compute='_get_work_hours')
    lack_hours = fields.Float('Lack Hours', compute='_get_lack_hours')
    reminder_id = fields.Many2one(
        'timesheet.reminder',
        'Reminder Timesheet',
        ondelete='cascade'
    )
    is_working_day = fields.Boolean(
        string='Is working day',
        compute='_check_is_working_day'
    )

    @api.multi
    @api.depends('reminder_date', 'reminder_id.employee_id')
    def _check_is_working_day(self):
        """
        Check the date belong to working day or rest day
        :return: if the check_date is working day return True,
        otherwise return False
        """
        public_holiday_obj = self.env['hr.holidays.public']
        for record in self:
            reminder_date_str = record.reminder_date
            reminder_date = fields.Date.from_string(reminder_date_str)
            employee_id = record.reminder_id.employee_id.id
            _is_weekend = True if reminder_date.weekday() in [5, 6] else False
            _is_public_holiday = public_holiday_obj.\
                is_public_holiday(reminder_date, employee_id=employee_id)
            record.is_working_day = not (_is_weekend or _is_public_holiday)

    @api.depends('reminder_date')
    def _get_leave_hours(self):
        """
        Get the leave time about every employee
        :return:
        """
        holiday_obj = self.env['hr.holidays']
        records = self.filtered(lambda x: x.is_working_day and x.reminder_id)
        for record in records:
            reminder_date_str = record.reminder_date
            _reminder_date = fields.Datetime.from_string(reminder_date_str)
            employee = record.reminder_id.employee_id
            reminder_date = fields.Datetime.context_timestamp(employee,
                                                              _reminder_date)
            work_on = fields.Datetime.\
                from_string(record.reminder_id.work_on_time).time()
            work_off = fields.Datetime.\
                from_string(record.reminder_id.work_off_time).time()

            leave_records = holiday_obj.search([
                ('employee_id', '=', employee.id),
                ('type', '=', 'remove'),
                ('state', 'not in', ['cancel', 'refuse']),
                ('date_from', '<=', reminder_date_str),
                ('date_to', '>=', reminder_date_str)
            ])
            result = 0.0
            for leave in leave_records:
                _start_leave = fields.Datetime.from_string(leave.date_from)
                start_leave = fields.Datetime.context_timestamp(employee,
                                                                _start_leave)
                _end_leave = fields.Datetime.from_string(leave.date_to)
                end_leave = fields.Datetime.context_timestamp(employee,
                                                              _end_leave)
                if start_leave.date() != reminder_date.date():
                    _sl = datetime.combine(reminder_date.date(), work_on)
                else:
                    _sl = start_leave if start_leave.hour >= work_on.hour \
                        else datetime.combine(reminder_date.date(), work_on)
                if end_leave.date() != reminder_date.date():
                    _el = datetime.combine(reminder_date.date(), work_off)
                else:
                    _el = end_leave if end_leave.hour <= work_off.hour \
                        else datetime.combine(reminder_date.date(), work_off)
                leave_hours = _el.hour - _sl.hour
                result += leave_hours if leave_hours > 0 else 0
            record.leave_hours = result

    @api.depends('reminder_date')
    def _get_work_hours(self):
        """
        Search the time sheet records to find out the employee TMS hours
        :return:
        """
        tms_obj = self.env['account.analytic.line']
        for record in self:
            tms_records = tms_obj.search([
                ('user_id', '=', record.reminder_id.employee_id.user_id.id),
                ('date', '=', record.reminder_date)
            ])
            res = 0.0
            for tms in tms_records:
                res += tms.unit_amount
            record.work_hours = res

    # @api.depends('leave_hours', 'work_hours')
    def _get_lack_hours(self):
        """
        Compute the hours the user didn't input in TMS
        :return:
        """
        for record in self:
            leave_hours = record.leave_hours or 0.0
            work_hours = record.work_hours or 0.0
            input_hours = record.reminder_id.work_hours
            lack_hours = input_hours - leave_hours - work_hours
            if record.is_working_day:
                record.lack_hours = lack_hours if lack_hours > 0 else 0
            else:
                record.lack_hours = 0.0


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
    work_on_time = fields.Datetime('Work On Time')
    work_off_time = fields.Datetime('Work Off Time')
    rest_hours = fields.Float('Rest Hours')
    work_hours = fields.Float('Work Hours', compute='_get_work_hours')
    count_days = fields.Integer('Count Days')

    @api.depends('work_on_time', 'work_off_time', 'rest_hours')
    def _get_work_hours(self):
        """
        compute how many hours the employee should input his TMS
        :return:
        """
        for record in self:
            work_on_time = fields.Datetime.from_string(record.work_on_time)
            work_off_time = fields.Datetime.from_string(record.work_off_time)
            total_work_hours = work_off_time.hour - work_on_time.hour
            record.work_hours = total_work_hours - record.rest_hours

    @api.model
    def _start_reminder(self, count_days, workstart, workend,
                        rest_hours, reminder_type=1):
        """
        The cron job start part, find the employee who didn't input his TMS and
         create the record for reminder his manager in the noon
        :param count_days: how many days need check
        :param workstart: the time when you start work(work on)
        :param workend: the time when you end work(work off)
        :param resethours: during the work time how many hours you get to reset
        :param reminder_type: Choose the email send to employee(1) or
        manager(2)
        :return:
        """
        reminder_records = self.env['timesheet.reminder']
        delta_one_day = timedelta(days=1)
        employee_records = self.env['hr.employee'].search([])
        _today = datetime.now()
        work_on = datetime.strptime(workstart, TIME_FORMAT)
        work_off = datetime.strptime(workend, TIME_FORMAT)
        for employee in employee_records:
            vals = {
                'employee_id': employee.id,
                'work_on_time': work_on,
                'work_off_time': work_off,
                'rest_hours': rest_hours or 0.0,
                'count_days': count_days,
                'reminder_date_ids': []
            }
            _yesterday = _today
            n = 0
            while n < count_days:
                _yesterday -= delta_one_day
                n += 1
                vals['reminder_date_ids'].append([0, False, {
                    'reminder_date': _yesterday.strftime(DATE_FORMAT)
                }])
            reminder_records |= self.create(vals)

        if reminder_type == 2:
            self._send_email_reminder_manager(reminder_records)
        else:
            self._send_email_reminder_employee(reminder_records)

        return True

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
            need_reminder = reminder.reminder_date_ids.\
                filtered(lambda x: x.lack_hours > 0)
            if not need_reminder:
                continue
            emp_work_email = reminder.employee_id.work_email
            if emp_work_email and email_from and \
                    (email_from != emp_work_email or force):
                mail_id = template.with_context(dbname=self.env.cr.dbname). \
                    send_mail(reminder.id)
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
        # Get the manger and employee mapping
        manager_employee_dict = {}
        for reminder in reminder_records:
            if reminder.employee_id.id == 7:
                pass
            manager = reminder.employee_id.parent_id
            if not manager:
                continue
            real_reminder = reminder.reminder_date_ids. \
                filtered(lambda x: x.lack_hours > 0)
            if not real_reminder:
                continue
            key = manager
            if key not in manager_employee_dict:
                manager_employee_dict[key] = {
                    'manager': manager,
                    'employee': {},
                    'res_id': reminder.id
                }
            reminder_date = (', ').join(
                [x.reminder_date for x in real_reminder])
            emp_key = (reminder.employee_id.id, reminder.employee_id.name)
            manager_employee_dict[key]['employee'][emp_key] = reminder_date

        for manager_record, real_content in manager_employee_dict.items():
            emp_work_email = manager_record.work_email
            res_id = real_content.pop('res_id')
            if emp_work_email and email_from and \
                    (emp_work_email != email_from or force):
                mail_id = template.with_context(manager=real_content). \
                    send_mail(res_id)
                the_mailmess = mail.browse(mail_id).mail_message_id
                the_mailmess.write({'model': None, 'res_id': False})
                mail_ids.append(mail_id)

        if mail_ids:
            res = mail.send(mail_ids)

        return res
