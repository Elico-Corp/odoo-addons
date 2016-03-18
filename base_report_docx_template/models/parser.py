# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.base_report_docx.report.report_docx import ReportDocx


class ReportDocxReport(ReportDocx):
    def generate_docx_data(self, cr, uid, ids, context):
        active_module = context['active_model']

        data = []
        for id in ids:
            module = self.pool.get(active_module).browse(
                cr, uid, id, context)
            data.append(self._obj2dict(module))

        return data

    def _obj2dict(self, obj):
        memberlist = [m for m in dir(obj)]
        context = {}
        for m in memberlist:
            if m[0] != "_" and not callable(m):
                context[m] = getattr(obj, m)

        return context

ReportDocxReport(
    'report.report.docx', 'report.docx.template',
)
