# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    allow_modification = fields.Boolean(
        'Allow Modification via Request'
    )


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.multi
    @api.depends('holiday_status_id')
    def _compute_allow_modification(self):
        self.ensure_one()
        self.allow_modification = self.holiday_status_id.allow_modification

    allow_modification = fields.Boolean(
        'Allow Modification via Request',
        compute="_compute_allow_modification"
    )
    modification_req_ids = fields.One2many(
        'allocation.modification.request',
        'leave_id',
        'Allocation Modification Requests'
    )

    @api.multi
    @api.depends('modification_req_ids')
    def _compute_request_pending_count(self):
        self.ensure_one()
        pending_states = []
        for req in self.modification_req_ids:
            if req.state not in ['approve', 'cancel']:
                pending_states.append(req.state)
        self.request_count = len(pending_states)

    request_count = fields.Integer(
        "Request count",
        compute="_compute_request_pending_count"
    )

    @api.multi
    def unlink(self):
        for hr in self:
            if hr.type == 'add' and (
                hr.allow_modification and hr.modification_req_ids
            ):
                for request in hr.modification_req_ids:
                    if request.state in ['confirm', 'approve', 'cancel']:
                            raise ValidationError(
                                _('You can only delete Allocation Request'
                                    ' Type Allow Request on Draft states'
                                    ' Please check linked Request.'))
        return super(HrHolidays, self).unlink()
