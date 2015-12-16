# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


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
