# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import time

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FRMT


class AllocationModificationRequest(models.Model):
    _name = "allocation.modification.request"
    _description = "Allocation Modification Request"
    _rec_name = "employee_id"
    _order = 'date desc'

    employee_id = fields.Many2one(
        "hr.employee",
        "Applicant",
        related='leave_id.employee_id',
        store=True
    )
    date = fields.Date(
        "Date",
        default=lambda *a: time.strftime(DATE_FRMT)
    )
    swap_day = fields.Date("Swap Day")
    leave_id = fields.Many2one(
        "hr.holidays",
        "Allocation request",
        ondelete='cascade'
    )
    number_of_days = fields.Float(
        "Number of Days",
        default=1
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled')],
        'State',
        default='draft',
        required=True
    )
    note = fields.Text(
        'Note'
    )

    _sql_constraints = [
        ('number_of_days_gt_zero', 'CHECK (number_of_days > 0)',
         _('Number of Days must be a positive number.'))
    ]

    def _get_status(self):
        if self._check_status_approved():
            return 'approve'
        if self._check_status_cancel():
            return 'cancel'
        if self._check_status_draft():
            return 'draft'
        return False

    @api.multi
    def _check_status_confirmed(self):
        for request in self:
            if request.state == 'confirm':
                return True
        return False

    @api.multi
    def _check_status_approved(self):
        for request in self:
            if request.state == 'approve':
                return True
        return False

    @api.multi
    def _check_status_cancel(self):
        for request in self:
            if request.state != 'cancel':
                return False
        return True

    @api.multi
    def _check_status_draft(self):
        for request in self:
            if request.state != 'draft':
                return False
        return True

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True

    @api.multi
    def action_set_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})
        if self.leave_id and self.leave_id.type == 'add':
            if self.leave_id.can_reset:
                req_ids = self.leave_id.modification_req_ids
                if req_ids._get_status() and (
                    req_ids._get_status() == 'draft'
                ):
                    # must be reset to draft the allocation request.
                    self.leave_id.holidays_reset()
                    if self.leave_id.number_of_days_temp > 0:
                        self.leave_id.number_of_days_temp -= \
                            self.number_of_days
        return True

    @api.multi
    def action_approve(self):
        self.ensure_one()
        self.write({'state': 'approve'})
        if self.leave_id and self.leave_id.type == 'add':
            # if leave_id.modification_req_ids:
            if self.leave_id.can_reset:
                req_ids = self.leave_id.modification_req_ids
                if req_ids._get_status() and (
                    req_ids._get_status() == 'approve'
                ):
                    # must be validate the allocation request.
                    if self.leave_id.state == 'draft':
                        self.leave_id.holidays_confirm()
                        self.leave_id.holidays_validate()
                    if self.leave_id.state == 'confirm':
                        self.leave_id.holidays_validate()
                    self.leave_id.number_of_days_temp += \
                        self.number_of_days
        return True

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def unlink(self):
        for request in self:
            if request.leave_id.state not in (
                ['draft', 'cancel', 'refuse']
            ) and request.state in ['confirm', 'approve', 'cancel']:
                    raise ValidationError(
                        _('You can only delete draft '
                            'Leave Type Modification Request.'))
        return super(AllocationModificationRequest, self).unlink()
