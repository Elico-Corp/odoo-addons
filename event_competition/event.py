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
from datetime import datetime
from openerp import models, fields, api
import uuid


class EventSerial(models.Model):
    """ Event Serial """
    _name = 'event.serial'
    _description = 'Event Serial'

    name = fields.Char('Name', size=16, compute='_compute_name', store=True)
    event_id = fields.Many2one(
        'event.event', string='Event', required=True,
        domain="[('state', '!=', 'done')]")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Done')
        ],
        string='State',
        default='draft'
    )
    used_date = fields.Datetime('Date Used')

    @api.depends('event_id')
    def _compute_name(self):
        name = None

        # Run until we have an unique number
        while True:
            name = str(uuid.uuid4()).replace('-', '')[0:16].upper()
            # Breaks when number is unique
            if not self.search([('name', '=', name)]):
                break
        self.name = name

    @api.one
    def confirm(self):
        now = str(datetime.now())
        self.write({'state': 'done', 'used_date': now})

    @api.one
    def cancel(self):
        self.write({'state': 'draft', 'used_date': None})


# Odoo offical class so i need to respect their class name convention.
class event_registration(models.Model):
    """ Event Registration """
    _inherit = 'event.registration'

    serial_id = fields.Many2one('event.serial', string="Serial", required=True)
    attachment = fields.Binary('Attachement')
    guardian_name = fields.Char('Guardian\'s name')
    address = fields.Text('Address')
    available = fields.Boolean('Available')
    terms = fields.Boolean('Has accepted terms')
    rate = fields.Selection(
        [('0', '0'), ('1', '1'), ('2', '2'),
         ('3', '3'), ('4', '4'), ('5', '5')],
        'Rate')

    @api.model
    def create(self, vals):
        res = super(event_registration, self).create(vals)
        # Confirm the serial key when the registration is created.
        if res:
            res.serial_id.confirm()
        return res

    @api.multi
    def unlink(self):
        # cancel serial
        for registration in self:
            registration.serial_id.cancel()
        return super(event_registration, self).unlink()
