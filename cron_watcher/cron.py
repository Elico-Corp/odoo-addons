# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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
from openerp.osv import orm
import time
from datetime import datetime
from openerp.tools.translate import _


class ir_cron(orm.Model):
    _name = 'ir.cron'
    _inherit = ['ir.cron', 'mail.thread']

    def _scheduler_cron_watcher(self, cr, uid, interval,
                                domain=None, context=None):
        interval *= 60
        m = self.pool.get('ir.model.data')
        cron_ids = self.search(cr, uid, [], context=context)
        date_format = "%Y-%m-%d %H:%M:%S"
        current_date = time.strftime(date_format)
        current_date = datetime.strptime(current_date, date_format)
        message_pool = self.pool.get('mail.message')

        group = m.get_object(
            cr, uid, 'cron_watcher', 'res_groups_cron_watcher')
        admin_user = m.get_object(
            cr, uid, 'base', 'user_root')
        partner_ids = [(4, user.partner_id.id) for user in group.users]
        for cron in self.browse(cr, uid, cron_ids, context=context):
            if not cron.nextcall:
                continue
            cron_date = datetime.strptime(cron.nextcall, date_format)
            delay = (current_date - cron_date).total_seconds()
            delay_minutes = round(int(delay) / 60)
            email = {
                'type': 'notification',
                'author_id': admin_user.partner_id.id,
                'partner_ids': partner_ids,
                'notified_partner_ids': partner_ids,
                'model': 'ir.cron',
                'res_id': cron.id,
                'subject': _('Cron Watcher Alert (%s)') % cron.name,
                'body': _(
                    'The cron job named "%s" has been delayed for\
                    more than %s minutes') % (cron.name, delay_minutes)
            }
            if delay > interval:
                message_pool.create(cr, uid, email, context=context)
