# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class TaskTimeSheet(models.Model):
    _name = 'extra.time.application'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    submit_user_id = fields.Many2one(
        'res.users', 'Applicant', help='Applicant',
    )
    task_no = fields.Many2one('project.task', 'Task No', help='Task No')
    reason = fields.Text('Reason', help='the reason of apply')
    apply_hours = fields.Float('Apply Hours', help='the length of apply time')
    state = fields.Selection([
        ('to_approve', 'To Approve'),
        ('approve', 'Approved'),
        ('refused', 'Refused'),
    ],track_visibility='onchange',defaule='to_approve')

    @api.one
    def approve_function(self):
        if self.state == 'to_approve':
            self.with_context(flag='True').task_no.remaining_hours += self.apply_hours
            self.task_no.sub_extra_time += self.apply_hours
            self.state = 'approve'
            self.message_post(body=('    Approved:%s'%self.env.user.name))

    @api.one
    def refuse_function(self):
        self.state = 'refused'

    @api.model
    def create(self, vals):
        msg_followers = []
        for user in self.env.ref('extra_time_application.group_extra_time_manager').users:
            if user != self.env['project.task'].browse(vals.get('task_no')).user_id:
                msg_vals = {
                    'partner_id': user.partner_id.id,
                    'res_model': self._name,
                }
                msg_followers.append((0, 0, msg_vals))


        task_id = self.env['project.task']. \
                    browse(vals.get('task_no'))
        task_manager = task_id.project_id.user_id
        if task_manager not in self.env.ref('extra_time_application.group_extra_time_manager').users and \
            task_manager != task_id.user_id:
            msg_vals = {
                'partner_id': task_manager.partner_id.id,
                'res_model': self._name,
            }
            msg_followers.append((0, 0, msg_vals))
        if msg_followers:
            vals['message_follower_ids'] = msg_followers
        return super(TaskTimeSheet, self).create(vals)

