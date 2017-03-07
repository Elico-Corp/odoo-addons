# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api, fields


class EventSerialGeneration(models.TransientModel):
    """ Event Serial Generation Wizard """
    _name = "event.serial.generation"
    _description = "Event Serial Generation Wizard"

    event_id = fields.Many2one(
        'event.event',
        string='Event', required=True)
    nb = fields.Integer('Number', required=True)

    @api.multi
    def generate(self):
        for obj in self:
            data = {'event_id': obj.event_id.id}
            for i in range(obj.nb):
                obj.env['event.serial'].create(data)
            return {'type': 'ir.actions.act_window_close'}
