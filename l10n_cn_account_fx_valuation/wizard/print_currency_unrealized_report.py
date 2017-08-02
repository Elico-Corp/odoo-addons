# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher / Eric CAUDAL
#    Copyright 2012 Camptocamp SA / Elico Corp
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
from osv import osv, fields

class UnrealizedCurrencyReportPrinter(osv.osv_memory):
    _name = "unrealized.report.printer"

    _columns = {'chart_account_id': fields.many2one('account.account', 'Chart root',
                                domain=[('parent_id', '=', False)],required=True),
               'period_id': fields.many2one('account.period', 'Period to use',required=True)}


    def print_report(self, cursor, uid, wid, data, context=None):
        context = context or {}
        # we update form with display account value
        if isinstance(wid, list):
            wid = wid[0]
        current = self.browse(cursor, uid, wid, context)
        form = {}
        form['period_id'] = current.period_id.id
        form['period_name'] = current.period_id.name
        form['account_ids'] = [current.chart_account_id.id]
        data['form'] = form

        return {'type': 'ir.actions.report.xml',
                'report_name': 'currency_unrealized',
                'datas': data}
UnrealizedCurrencyReportPrinter()
