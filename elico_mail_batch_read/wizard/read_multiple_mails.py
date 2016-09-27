# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Rona Lin <rona.lin@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
