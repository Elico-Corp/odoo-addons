# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

try:
    import xlwt
except ImportError, e:
    pass

from openerp import SUPERUSER_ID
from openerp.addons.report_xls.report_xls import report_xls
from openerp.report import report_sxw
from openerp.tools.translate import translate

_logger = logging.getLogger(__name__)

_ir_translation_name = 'report.hr.payroll.report.xls'


class ReportHrPayrollParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportHrPayrollParser, self).__init__(
            cr, uid, name, context=context)
        sche_obj = self.pool.get('hr.payslip.run')
        self.context = context
        wanted_list = sche_obj._report_xls_fields(cr, uid, context)
        template_changes = sche_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report',
                         lang, src) or src


class ReportHrPayroll(report_xls):

    # write table head
    def table_head(self, ws, style0, style1):
        """
            generate fixed table head,return title_list and col number
        """
        ws.write_merge(1, 2, 0, 0, u'序号', style1)
        ws.write_merge(1, 2, 1, 1, u'年月', style1)
        ws.write_merge(1, 2, 2, 2, u'姓 名', style1)
        ws.write_merge(1, 2, 3, 3, u'职位', style1)
        col = 3
        title_list = ['month', 'name', 'job_title']
        return title_list, col

    def table_head_info(self, ws, col, rule_group, title_list, style1):
        """
            auto generate table head,return title_list and col number
        """
        if len(rule_group['rules']) == 1:
            col += 1
            ws.write_merge(1, 2, col, col, rule_group['category'], style1)
            title_list.append(rule_group['rules'][0].name)
        else:
            merge_col = col + 1
            if rule_group['type'] == 'add':
                col += 1
                ws.write(2, col, u'小计', style1)
                title_list.append('add_total')
            elif rule_group['type'] == 'sub':
                col += 1
                ws.write(2, col, u'小计', style1)
                title_list.append('sub_total')
            rules = []
            for rule in rule_group['rules']:
                obj_dict = {}
                obj_dict['name'] = rule.name
                obj_dict['sequence'] = rule.sequence
                rules.append(obj_dict)
            # sorted by rule sequence
            rules = sorted(rules, key=lambda x: x['sequence'])
            for rule in rules:
                col += 1
                ws.write(2, col, rule['name'], style1)
                title_list.append(rule['name'])
            ws.write_merge(
                1, 1, merge_col, col, rule_group['category'], style1)
            if rule_group['type'] == 'add':
                col += 1
                ws.write_merge(1, 2, col, col, u'应发工资', style1)
                title_list.append('should_paid')
            elif rule_group['type'] == 'sub':
                col += 1
                ws.write_merge(1, 2, col, col, u'实发工资', style1)
                title_list.append('real_wage')
        return title_list, col

    def table_title(self, ws, col, title, style0, style1):
        """
            generate table title,return col number
        """
        col += 1
        ws.write_merge(1, 2, col, col, u'备注', style1)
        ws.write_merge(0, 0, 0, col, title, style0)
        col += 1
        ws.row(0).height = 255 * 3
        return col

    # write table information
    def table_info(self, ws, num, result, title_list, style1):
        """
            generate table information,return row number
        """
        number = 0
        for number, res in enumerate(result):
            ws.write(num, 0, number + 1, style1)
            for title in title_list:
                ws.write(num, title_list.index(title) + 1, res[title], style1)
            ws.write(num, title_list.index(title) + 2, '', style1)
            num += 1
        return num

    def table_foot(self, ws, num, col, style1, style2):
        """
            generate table foot,return row number
        """
        ws.write_merge(num, num, 0, 3, u'合     计', style1)
        for number in range(4, col):
            ws.write(num, number, '', style1)
        num += 1
        ws.write_merge(num, num, 0, 2, u'负责人：', style2)
        ws.write_merge(num, num, 3, 5, u'出纳：', style2)
        ws.write_merge(num, num, 6, 8, u'会计：', style2)
        ws.write_merge(num, num, 9, 11, u'制表：', style2)
        ws.write_merge(num, num, 12, 14, u'制表：', style2)
        num += 1
        return num

    def get_job_title(self, obj):
        """
            return job title
        """
        if obj.employee_id.job_id and obj.employee_id.job_id.name:
            return obj.employee_id.job_id.name
        else:
            return ''

    def xls_format(self):
        '''
        return xls style
        @return style0, style1, style2
        '''
        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        borders.bottom_colour = 0x3A

        font0 = xlwt.Font()
        font0.name = 'Arial'
        font0.height = 350
        font0.bold = True
        font0.underline = True

        font1 = xlwt.Font()
        font1.name = 'Arial'
        font1.height = 200

        # center
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER

        # for title
        style0 = xlwt.XFStyle()
        style0.font = font0
        style0.alignment = alignment

        style1 = xlwt.XFStyle()
        style1.font = font1
        style1.borders = borders
        style1.alignment = alignment

        style2 = xlwt.XFStyle()
        style2.font = font1
        style2.alignment = alignment
        return style0, style1, style2

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        """
            generate hr payslip report
        """
        style0, style1, style2 = self.xls_format()
        ws = wb.add_sheet('Sheet1')
        rule_groups = []
        result = []
        num = 3
        slip_objs = objects.slip_ids
        # if not have payslip,display empty file
        if slip_objs:
            # satisfy the condition
            categorys = slip_objs[0].struct_id.rule_ids.read_group(
                [('appear_on_report', '=', True),
                 ('id', 'in', slip_objs[0].struct_id.rule_ids.ids)],
                [], ['category_id'])
            title_list, col = self.table_head(ws, style0, style1)
            for category in categorys:
                groups = {}
                rule_ids = self.pool.get('hr.salary.rule').search(
                    self.cr, SUPERUSER_ID, category['__domain'])
                rules = self.pool.get('hr.salary.rule').browse(
                    self.cr, SUPERUSER_ID, rule_ids)
                groups['rules'] = rules
                groups['sequence'] = rules[0].category_id.sequence_number
                groups['category'] = rules[0].category_id.name
                groups['type'] = rules[0].category_id.category_type
                rule_groups.append(groups)
            # sorted by rule category sequence
            rule_groups = sorted(rule_groups, key=lambda x: x['sequence'])
            for rule_group in rule_groups:
                title_list, col = self.table_head_info(
                    ws, col, rule_group, title_list, style1)
            col = self.table_title(ws, col, objects.name, style0, style1)
            for slip in slip_objs:
                obj_dict = {}
                obj_dict['month'] = slip.date_from
                obj_dict['name'] = slip.employee_id.name_related
                obj_dict['job_title'] = self.get_job_title(slip)
                obj_dict['remarks'] = ''
                add_total = 0.0
                sub_total = 0.0
                basic_total = 0.0
                for rule in slip.details_by_salary_rule_category:
                    obj_dict[rule.name] = rule.total
                    if rule.category_id.category_type == 'add':
                        add_total += rule.total
                    if rule.category_id.category_type == 'sub':
                        sub_total += rule.total
                    if rule.category_id.category_type == 'basic':
                        basic_total += rule.total
                obj_dict['add_total'] = add_total
                obj_dict['should_paid'] = basic_total + add_total
                obj_dict['sub_total'] = sub_total
                obj_dict['real_wage'] = basic_total + add_total + sub_total
                result.append(obj_dict)
            num = self.table_info(ws, num, result, title_list, style1)
            num = self.table_foot(ws, num, col, style1, style2)

ReportHrPayroll(
    'report.report.hr.payroll.report.xls', 'hr.payslip.run',
    parser=ReportHrPayrollParser)
