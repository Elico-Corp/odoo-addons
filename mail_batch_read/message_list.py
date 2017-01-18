# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class MessageList(models.Model):
    _inherit = 'mail.message'

    body_size_200 = fields.Html('body', compute="_compute_borrowable")

    @api.depends('body')
    @api.one
    def _compute_borrowable(self):
        if self.body:
            self.body_size_200 = self.body[0:200]
