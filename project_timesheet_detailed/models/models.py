# -*- coding: utf-8 -*-
# © 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    stage = fields.Selection(
        selection=[
            ('fixed', 'Fixed'),
            ('to review', 'To review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='to review',

    )
    estimated_time = fields.Float(
        'Estimated time', compute='_compute_estimated_time')
    approved_time = fields.Float(
        'Approved time', compute='_compute_approved_time')

    @api.multi
    @api.depends('task_id')
    def _compute_estimated_time(self):
        for rec in self:
            if rec.task_id:
                rec.estimated_time = rec.task_id.planned_hours

    @api.multi
    @api.depends('task_id')
    def _compute_approved_time(self):
        for rec in self:
            if rec.task_id:
                approved_tms = rec.env['account.analytic.line'].search(
                    [('task_id', '=', rec.task_id.id)]).filtered(
                    lambda rec: rec.stage == 'approved')
                rec.approved_time = \
                    sum([tms.unit_amount for tms in approved_tms])

    @api.multi
    def set_approved(self):
        current_user = self.env.user
        for rec in self:
            if (current_user == rec.project_id.user_id) or (
                current_user ==
                    rec.user_id.employee_ids.parent_id.user_id):
                rec.stage = 'approved'
            else:
                raise UserError(
                    'You do not have permission to approve it')

    @api.multi
    def set_rejected(self):
        current_user = self.env.user
        for rec in self:
            if (current_user == rec.project_id.user_id) or (
                current_user ==
                    rec.user_id.employee_ids.parent_id.user_id):
                rec.stage = 'rejected'
                mail = self.env['mail.mail'].create({
                    'body_html': 'Your TMS %s was turn down' % (rec.name),
                    'email_to': rec.user_id.login,
                    'subject': 'Reject TMS',
                })
                mail.send()
            else:
                raise UserError(
                    'You do not have permission to reject it')

    @api.multi
    def set_review(self):
        current_user = self.env.user
        for rec in self:
            if (current_user == rec.project_id.user_id) or (
                current_user ==
                    rec.user_id.employee_ids.parent_id.user_id):
                rec.stage = 'to review'
            else:
                raise UserError(
                    'You do not have permission to change the state')

    @api.onchange('project_id')
    def onchange_project_id(self):
        eml = self.task_id
        res = super(AccountAnalyticLine, self).onchange_project_id()
        self.task_id = eml
        return res

    @api.onchange('task_id')
    def task_id_on_change(self):
        if self.task_id:
            self.project_id = self.task_id.project_id.id

    @api.onchange('issue_id')
    def issue_id_on_change(self):
        if self.issue_id:
            self.project_id = self.issue_id.project_id.id

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.stage == 'rejected' and vals:
                vals['stage'] = 'fixed'
            if vals.get('task_id'):
                vals.update({
                    'project_id':
                        self.env['project.task'].search([
                            ('id', '=', vals.get('task_id'))]).project_id.id})
            if vals.get('issue_id'):
                vals.update(
                    {'project_id': self.env['project.issue'].search(
                        [('id', '=', vals.get('issue_id'))]).project_id.id})
        return super(AccountAnalyticLine, self).write(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.stage != 'to review':
                raise UserError('Only records in to review can be deleted!')
        return super(AccountAnalyticLine, self).unlink()

    @api.multi
    @api.constrains('task_id', 'issue_id')
    def _check_task_and_issue(self):
        if self.task_id and self.issue_id:
            raise ValueError(
                'It is not allowed to have task and issue at the same time.')
