# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (http://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

from common_method import *


class TimesheetReport(models.TransientModel):
    _name = "timesheet.manager.remind.employee"
    _description = "Timesheet Manager Remind Employee list"

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee'
    )

    manager_id = fields.Many2one(
        string='Manager',
        comodel_name='timesheet.manager.remind'
    )

    date_reminder = fields.Char(
        string='Reminding date'
    )


class TimesheetReport(models.TransientModel):
    _name = "timesheet.manager.remind"
    _description = "Timesheet Manager Remind Service"
    _inherit = ['mail.thread']

    manager_id = fields.Many2one(
        string='Manager',
        comodel_name='hr.employee'
    )

    employee_list = fields.One2many(
        'timesheet.manager.remind.employee',
        'manager_id',
        string='Employee list'
    )

    created_date = fields.Char(
        string='Create date'
    )

    @api.multi
    def _check_weekend_or_holiday(
            self,
            selected_date=False,
            employee_id=False
    ):
        publicholiday = self.env['hr.holidays.public']
        if not publicholiday.is_public_holiday(
                selected_date,
                employee_id
        ) \
                and not is_weekend(
                    selected_date
        ):
            return True
        else:
            return False

    @api.multi
    def _remind_manager_workhours(
            self,
            manager_remind_list=False,
            selected_date=False,
            employee=False,
            resethours=False,
            allhours_expected=False,
    ):
        hranalytictmobj = self.env['hr.analytic.timesheet']
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
                manager_remind_list[
                    len(manager_remind_list) - 1
                ]['date'].append(str(selected_date))
                if employee.parent_id:
                    manager_remind_list[
                        len(manager_remind_list) - 1
                    ]['manager_id'] = employee.parent_id.id
        else:
            manager_remind_list[
                len(manager_remind_list) - 1
            ]['date'].append(str(selected_date))
            if employee.parent_id:
                manager_remind_list[
                    len(manager_remind_list) - 1
                ]['manager_id'] = employee.parent_id.id

    @api.multi
    def _create_remind_list_object(
            self,
            manager_remind_list,
    ):
        employee_with_manager_list = filter(
            lambda employee: 'manager_id' in employee,
            manager_remind_list
        )
        manager_list = set([employee['manager_id'] for employee in
                            employee_with_manager_list])
        for manager in manager_list:
            employee_remind_list = []
            employee_with_specific_manager_list = filter(
                lambda employee: employee['manager_id'] == manager,
                employee_with_manager_list
            )
            for employee in employee_with_specific_manager_list:
                employee_remind_list.append(
                    (
                        0, False,
                        {
                            'employee_id': employee['employee_id'],
                            'date_reminder': ", ".join(employee['date'])
                        }
                    )
                )
            self.create(
                {
                    'manager_id': employee['manager_id'],
                    'created_date': str(
                        tz_offset_today(self.env.user.tz)
                    ),
                    'employee_list': employee_remind_list
                }
            )
        return manager_list

    @api.model
    def _start_remind(
            self,
            count_days=7,
            workstart='9:00:00',
            workend='18:00:00',
            resethours=1
    ):
        manager_remind_list = []
        employee_list = self.env['hr.employee'].search([])
        for employee in employee_list:
            count = 0
            selected_date = tz_offset_today(self.env.user.tz)
            date_one_day = timedelta(days=1)
            manager_remind_list.append({
                'employee_id': employee.id,
                'date': [],
            })
            while count < count_days:
                selected_date = selected_date - date_one_day
                if self._check_weekend_or_holiday(
                        selected_date,
                        employee.id
                ):
                    allhours_expected = self._get_all_hour(
                        selected_date,
                        employee.id,
                        workstart,
                        workend,
                        resethours
                    )
                    if allhours_expected:
                        self._remind_manager_workhours(
                            manager_remind_list,
                            selected_date,
                            employee,
                            resethours,
                            allhours_expected,
                        )
                        count += 1
        manager_list = self._create_remind_list_object(
            manager_remind_list
        )
        self.send_email_manager(manager_list)

    @api.multi
    def send_email_manager(
            self,
            manager_list=False,
            template_xmlid='manager_reminder_email_template',
            force=False
    ):
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
        for manager_id in manager_list:
            for manager in self.search([
                    ('manager_id', '=', manager_id),
                    ('created_date', '=', str(
                        tz_offset_today(self.env.user.tz))
                     )
            ]):
                email_from = self.env.user.company_id.email
                if manager.manager_id.work_email and email_from and (
                        manager.manager_id.work_email != email_from or
                        force):
                    mail_id = template.send_mail(self.env.cr,
                                                 self.env.uid,
                                                 template_id,
                                                 manager.id,
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
            str(selected_date) + ' ' + str(workstart),
            tz_info=standard_tz)
        selected_date_end = str_to_datetime(
            str(selected_date) + ' ' + str(workend),
            tz_info=standard_tz)
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
