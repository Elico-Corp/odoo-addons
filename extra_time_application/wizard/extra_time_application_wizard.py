# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models, api


class TimePromptBox(models.TransientModel):
    _name = 'extra.time.application.wizard'

    @api.model
    def _get_task_no(self):
        return self.env['project.task'].browse(
            self._context.get('active_id')
        )

    submit_user_id = fields.Many2one(
        'res.users', 'Applicant', help='Applicant',
        default=lambda self: self.env.user, readonly="True"
    )
    task_no = fields.Many2one('project.task', 'Task No', help='Task No',
                              default=_get_task_no, readonly="True"
                              )
    reason = fields.Text('Reason', help='the reason of apply')
    apply_hours = fields.Float('Apply Hours', help='the length of apply time')

    @api.multi
    def subscribe(self):
        user = self.env.user
        is_exist = user.has_group(
            'extra_time_application.group_project_task_manager')
        if is_exist:
            self.env['extra.time.application'].create({
                'submit_user_id': self.submit_user_id.id,
                'task_no': self.task_no.id,
                'reason': 'Automaticity create From PM or Reviewer',
                'apply_hours': self.apply_hours,
                'state': 'approve',
            })
            self.task_no.remaining_hours += self.apply_hours
            self.task_no.sub_extra_time += self.apply_hours

        else:
            mail = self.env['mail.mail'].create({
                'body_html': 'apply time:' + str(
                    self.apply_hours) + '<br>reason:' +
                str(self.reason) + '<br>Task:' +
                str(self.task_no.code),
                'email_to': self.task_no.project_id.user_id.login,
                'subject': 'Apply Time',
            })
            mail.send()
            self.env['extra.time.application'].create({
                'submit_user_id': self.submit_user_id.id,
                'task_no': self.task_no.id,
                'reason': self.reason,
                'apply_hours': self.apply_hours,
                'state': 'to_approve',
            })
