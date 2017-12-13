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
    ])

    @api.one
    def approve_function(self):
        if self.state == 'to_approve':
            self.task_no.remaining_hours += self.apply_hours
            self.task_no.sub_extra_time += self.apply_hours
            self.state = 'approve'

    @api.one
    def refuse_function(self):
        self.state = 'refused'
