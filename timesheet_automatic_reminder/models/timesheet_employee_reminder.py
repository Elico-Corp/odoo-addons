# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

from common_method import *


class TimesheetReport(models.TransientModel):
    _name = "timesheet.employee.reminder.date"
    _description = "Timesheet Employee Reminder Date"

    reminder_date = fields.Char(
        string='Reminder Date',
    )

    employee_remind_id = fields.Many2one(
        string='Reminding Employee',
        comodel_name='timesheet.employee.reminder'
    )


class TimesheetReport(models.TransientModel):
    _name = "timesheet.employee.reminder"
    _description = "Timesheet Employee Reminder Service"
    _inherit = ['mail.thread']

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
    )

    created_date = fields.Char(
        string='Creation date',
    )

    date_list = fields.One2many(
        'timesheet.employee.reminder.date',
        'employee_remind_id',
        string='Date list'
    )

    @api.multi
    def _check_is_working_day(
            self,
            selected_date,
            employee_id=False
    ):
        """
        Check the date belong to working day or rest day
        :param selected_date: the date need to checked
        :param employee_id:
        :return:
        """
        publicholiday = self.env['hr.holidays.public']
        return not (
            publicholiday.is_public_holiday(
                selected_date,
                employee_id=employee_id
            ) or is_weekend(selected_date)
                    )

    @api.multi
    def _create_remind_list_object(
            self,
            employee_remind_list
    ):
        for employee, datelist in employee_remind_list.items():
            self.create(
                {
                    'employee_id': employee,
                    'created_date': str(
                        tz_offset_today(self.env.user.tz)
                    ),
                    'date_list': datelist
                }
            )

    @api.multi
    def _check_employee_workhours(
            self,
            employee_remind_list,
            selected_date=False,
            employee=False,
            resethours=False,
            allhours_expected=False,
    ):
        hranalytictmobj = self.env['hr.analytic.timesheet']
        hrworklist = hranalytictmobj.search([
            ('date', '=', str(selected_date)),
            ('user_id', '=', employee.user_id.id)
        ])
        if hrworklist:
            workhours_real = 0
            for hrwork in hrworklist:
                workhours_real += hrwork.unit_amount
            allhours_real = workhours_real + resethours
            if allhours_expected > allhours_real:
                employee_remind_list[employee.id].append(
                    (0, False, {'reminder_date': str(selected_date)})
                )
        else:
            employee_remind_list[employee.id].append(
                (0, False, {'reminder_date': str(selected_date)})
            )

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
        for employee in employee_list:
            count = 0
            selected_date = tz_offset_today(self.env.user.tz)
            date_one_day = timedelta(days=1)
            employee_remind_list[employee.id] = []
            while count < count_days:
                selected_date = selected_date - date_one_day
                if self._check_is_working_day(
                        selected_date,
                        employee_id=employee.id
                ):
                    allhours_expected = self._get_all_hour(
                        selected_date,
                        employee.id,
                        workstart,
                        workend,
                        resethours
                    )
                    if allhours_expected:
                        self._check_employee_workhours(
                            employee_remind_list,
                            selected_date,
                            employee,
                            resethours,
                            allhours_expected,
                        )
                        count += 1
        self._create_remind_list_object(employee_remind_list)
        self.send_email_employee()

    @api.multi
    def send_email_employee(
            self,
            template_xmlid='employee_reminder_email_template',
            force=False
    ):
        email_from = self.env.user.company_id.email
        mail_ids = []
        data = self.env['ir.model.data']
        mailmess = self.pool['mail.message']
        mail = self.env['mail.mail']
        template = self.pool['email.template']
        local_context = self._context.copy()
        dummy, template_id = data.get_object_reference(
            'timesheet_automatic_remind',
            template_xmlid
        )
        local_context.update({
            'dbname': self.env.cr.dbname,
        })

        for employee in self.search([
            ('created_date',
             '=',
             str(tz_offset_today(self.env.user.tz)),
             )]
        ):
            if employee.employee_id.work_email and email_from and (
                    employee.employee_id.work_email != email_from or force):
                mail_id = template.send_mail(self.env.cr,
                                             self.env.uid,
                                             template_id,
                                             employee.id,
                                             context=local_context)
                vals = {}
                vals['model'] = None
                vals['res_id'] = False
                the_mailmess = mail.browse(mail_id).mail_message_id
                mailmess.write(self.env.cr,
                               self.env.uid,
                               [the_mailmess.id],
                               vals,
                               context=self._context)
                mail_ids.append(mail_id)

        if mail_ids:
            res = mail.send(mail_ids)

        return res

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
        selected_date_start = str_to_datetime(
            str(selected_date) + ' ' + str(workstart), tz_info=standard_tz)
        selected_date_end = str_to_datetime(
            str(selected_date) + ' ' + str(workend), tz_info=standard_tz)
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
            leave_date_from = str_to_datetime(
                leave.date_from, new_tz=employee_tz
            )
            leave_date_to = str_to_datetime(
                leave.date_to, new_tz=employee_tz
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
