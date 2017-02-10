# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class HrContractCn(models.Model):
    _inherit = 'hr.contract'

    social_insurance_amount = fields.Float(
        'Social Insurance Base',
        digits_compute=dp.get_precision('Payroll')
    )
    pit_base_amount = fields.Float(
        'PIT Base',
        digits_compute=dp.get_precision('Payroll'),
        default=0
    )

    @api.one
    @api.constrains('pit_base_amount')
    def _pit_base_amount_check(self):
        if not self.pit_base_amount > 0:
            raise ValidationError(_('PIT Base must be greater than 0.'))


class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    name = fields.Char('Name', required=True, translate=True)


class HrSalaryRuleCategory(models.Model):
    _inherit = "hr.salary.rule.category"

    name = fields.Char('Name', required=True, translate=True)


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"
    _order = "sequence"

    name = fields.Char('Name', required=True, translate=True)


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"
    _order = "sequence"
