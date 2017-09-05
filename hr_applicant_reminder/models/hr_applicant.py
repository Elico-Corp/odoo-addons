# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FRMT


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    @api.model
    def _remind_applicant_due(self):
        """
        This method sends notification to followers regarding applicant action
        """
        curent_date = datetime.now()
        hours = 48
        # Check day of the current date. If it is Thu or Fri take 96 hrs
        if curent_date.strftime('%a') in ['Thu', 'Fri']:
            hours = 96
        # Add 48 or 96 hrs in the current date and get future date
        next_action_date = (curent_date +
                            relativedelta(hours=hours)).strftime(DATE_FRMT)
        # Search for applicants based on Next Action Date
        applicants = self.env['hr.applicant'].search([('date_action', '=',
                                                       next_action_date)])
        # Email Template
        app_template =\
            self.env.ref('hr_applicant_reminder.mail_template_due_applicant')
        mail_obj = self.env['mail.mail']
        mail_ids = []
        for applicant in applicants:
            mail_id = app_template.send_mail(applicant.id, force_send=False,
                                             raise_exception=False)
            mail_ids.append(mail_ids)
            mail = mail_obj.browse(mail_id)
            # Add follower partners in mail recipients
            mail.write({
                'recipient_ids': [(6, 0, [follower.partner_id.id
                                          for follower in
                                          applicant.message_follower_ids
                                          if follower.partner_id])]})
            # Send mail forcefully
            mail.send()
        return mail_ids
