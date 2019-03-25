# -*- coding: utf-8 -*-
#   2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.osv import orm
import time
from datetime import datetime
from openerp.tools.translate import _


class IrCron(orm.Model):
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
