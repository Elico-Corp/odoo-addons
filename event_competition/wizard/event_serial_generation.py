# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Augustin Cisterne-Kaas
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
from openerp import models, api, fields


class EventSerialGeneration(models.TransientModel):
    """ Event Serial Generation Wizard """
    _name = "event.serial.generation"
    _description = "Event Serial Generation Wizard"

    event_id = fields.Many2one(
        'event.event',
        string='Event', required=True)
    nb = fields.Integer('Number', required=True)

    @api.one
    def generate(self):
        data = {'event_id': self.event_id.id}
        for i in range(self.nb):
            self.env['event.serial'].create(data)
        return {'type': 'ir.actions.act_window_close'}
