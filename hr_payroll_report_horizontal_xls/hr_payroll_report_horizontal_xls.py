# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia<liu.lixia@elico-corp.com>
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


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def payroll_report(self):
        '''
        general description.

        @return:
        '''
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.hr.payroll.report.xls',
            'report_type': 'xls',
            'datas': {},
        }

    def _report_xls_fields(self, cr, uid, context=None):
        return []

    # Change/Add Template entries
    def _report_xls_template(self, cr, uid, context=None):
        return {}


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    appear_on_report = fields.Boolean(String='Appear On Report', default=False)


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    sequence_number = fields.Integer(String='Report Sequence')
    category_type = fields.Selection(
        selection=[('add', u'add_item'), ('sub', u'sub_item'),
                   ('basic', u'basic'), ('none', 'None')],
        String='type', required=True, default='none')
