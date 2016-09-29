# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models
from openerp import api


class MailMessageRead(models.TransientModel):
    _name = "mail.message.read"
    _description = "Read multiple Mails"

    @api.multi
    def readmails(self):
        obj_mail = self.env['mail.message']
        msg_ids = self.env.context.get('active_ids', [])
        mail = obj_mail.browse(msg_ids)
        mail.set_message_read(read=True, create_missing=True)
