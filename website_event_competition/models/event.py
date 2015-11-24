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
import base64
from openerp import models, api
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class event_registration(models.Model):
    """ Event Registration """
    _inherit = 'event.registration'

    def _check_required_fields(self, post):
        fields = set(
            ['serial_id', 'name', 'guardian_name', 'phone', 'email',
             'attachment', 'address', 'available', 'terms']
        )
        res = fields - set(post.keys())
        if res:
            raise Exception(','.join(res))

    def _convert_attachement(self, attachment):
        try:
            return base64.encodestring(attachment.read())
        except Exception:
            raise('attachement')

    def _get_valid_serial(self, name):
        _logger.info("Trying serial number '%s'.", name.upper())
        serials = self.env['event.serial'].sudo().search([
            ('name', '=', name.upper()),
            ('state', '=', 'draft'),
            ('event_id.state', '!=', 'done')]
        )
        if not serials:
            _logger.warning("Wrong serial number '%s'.", name.upper())
            raise Exception('serial_id')
        return serials[0]

    @api.model
    def form_create(self, post):
        # Duplicate the array cause we need to modify it
        try:
            self._check_required_fields(post)
            attachment = self._convert_attachement(post['attachment'])
            serial = self._get_valid_serial(post['serial_id'])
            self.send_form_mail(post, attachment, True)
        except Exception, e:
            self.send_form_mail(post, attachment, False)
            raise e
        post.update(
            {'serial_id': serial.id,
             'event_id': serial.event_id.id, 'attachment': attachment})
        return self.sudo().create(post)

    def send_form_mail(self, post, attachment_data, success):
        success = _('SUCCESS') if success else _('FAILED')
        mail_pool = self.env['mail.mail'].sudo()
        admin_user = self.env.ref('base.user_root')
        group = self.env.ref('marketing.group_marketing_manager')
        partner_ids = [(4, user.partner_id.id) for user in group.users]
        attachment = {
            'name': post['attachment'].filename,
            'datas': attachment_data,
            'partner_id': admin_user.partner_id.id
        }
        email = {
            'type': 'email',
            'partner_ids': partner_ids,
            'recipient_ids': partner_ids,
            'attachment_ids': [(0, 0, attachment)],
            'subject': _(
                '[SC][REGISTRATION][%s][%s]') % (
                post['serial_id'].upper(), success),
            'auto_delete': True,
            'body_html': _(
                '''<p>The following submission has been made:</p>
                    <ul>
                    <li>Name: %s</li>
                    <li>Guardian: %s</li>
                    <li>Phone: %s</li>
                    <li>Email: %s</li>
                    <li>Address: %s</li>
                    <li>Available: %s</li>
                    <li>Accepted Terms: %s</li>
                    </ul>''' % (
                    post['name'], post['guardian_name'],
                    post['phone'], post['email'], post['address'],
                    post['available'], post['terms']))
        }
        mail = mail_pool.create(email)
        mail.send()
