# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FRMT


class TestAllocationModificationRequest(common.TransactionCase):

    def setUp(self):
        super(TestAllocationModificationRequest, self).setUp()
        self.applicant_obj = self.env['hr.applicant']
        self.employee = self._create_applicants()
        self.root_user = self.env.ref('base.user_root')
        self._subscribe_users()

    def _create_applicants(self):
        """Create the Applicants."""
        curent_date = datetime.now()
        next_action_date_1 = (curent_date +
                              relativedelta(hours=48)).strftime(DATE_FRMT)
        next_action_date_2 = (curent_date +
                              relativedelta(hours=96)).strftime(DATE_FRMT)
        self.applicant1 = self.applicant_obj.create({
            'name': 'Project Manager',
            'partner_name': 'Applicant 1',
            'date_action': next_action_date_1,
            'title_action': 'Send mail regarding our interview',
        })
        self.applicant2 = self.applicant_obj.create({
            'name': 'Sales Manager',
            'partner_name': 'Applicant 2',
            'date_action': next_action_date_2,
            'title_action': 'Call to define real needs about training',
        })
        self.applicant3 = self.applicant_obj.create({
            'name': 'Account Manager',
            'partner_name': 'Applicant 3',
            'date_action': next_action_date_1,
            'title_action': 'Send mail regarding our interview',
        })

    def _subscribe_users(self):
        """Add follower to applicants"""
        self.applicant1.message_subscribe_users([self.root_user.id])
        self.applicant2.message_subscribe_users([self.root_user.id])
        self.applicant3.message_subscribe_users([self.root_user.id])

    def test_remind_applicant_due(self):
        """Check if mails have been sent to followers."""
        mail_ids = self.applicant_obj._remind_applicant_due()
        self.assertTrue(len(mail_ids) > 0,
                        "E-mails should be sent to the followers.")
