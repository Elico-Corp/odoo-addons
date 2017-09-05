# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp.tests import common


class TestAllocationModificationRequest(common.TransactionCase):

    def setUp(self):
        super(TestAllocationModificationRequest, self).setUp()
        self.allocation_req_obj = self.env['allocation.modification.request']
        self.leave_type_obj = self.env['hr.holidays.status']
        self.user_obj = self.env['res.users']
        self.res_employee = self.env['hr.employee']
        self.holiday_obj = self.env['hr.holidays']
        self.company = self.env.ref('base.main_company')
        self.grp_hr_manager = self.env.ref('base.group_hr_manager')
        self.user = self._create_user('user_1', [self.grp_hr_manager],
                                      self.company)
        self.employee = self._create_employee()
        self.leave_type = self._create_leave_type()
        self.leave_allocation = self._create_leave_allocation()
        self.alloc_modification_req = self._create_alloc_modification_request()

    def _create_user(self, login, groups, company, context=None):
        """Create a user."""
        group_ids = [group.id for group in groups]
        return self.user_obj.create({
            'name': 'Test User',
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, group_ids)]
        })

    def _create_employee(self):
        """Create an employee."""
        return self.res_employee.create({
            'name': 'Test Employee',
            'user_id': self.user.id
        })

    def _create_leave_type(self):
        """Create Leave Type"""
        return self.leave_type_obj.create({
            'name': 'Test Leave Type',
            'allow_modification': True,
        })

    def _create_leave_allocation(self):
        """Allocate leaves to employee."""
        leave_allocation = self.holiday_obj.create({
            'name': 'Test Leave Allocation',
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_type.id,
            'number_of_days_temp': 5,
            'holiday_type': 'employee',
            'type': 'add',
        })
        # Confirm leave allocation
        leave_allocation.signal_workflow('confirm')
        # Validate leave allocation
        leave_allocation.signal_workflow('validate')
        return leave_allocation

    def _create_alloc_modification_request(self):
        """Create Allocation Modification Request"""
        allocation_modification_req = self.allocation_req_obj.create({
            'employee_id': self.employee.id,
            'leave_id': self.leave_allocation.id,
            'number_of_days': 2,
        })
        allocation_modification_req.action_confirm()
        allocation_modification_req.action_approve()
        return allocation_modification_req

    def test_request_leave_addition(self):
        """Check whether request days have been added in allocated leaves."""
        self.assertFalse(self.leave_allocation.number_of_days_temp != 7,
                         "Requested days didn't add in allocation.")

    def test_security(self):
        """Check if employee has access to leave type modification request."""
        self.assertTrue(self.alloc_modification_req.id,
                        "Employee should have access of Leave Type"
                        " Modification Request.")
