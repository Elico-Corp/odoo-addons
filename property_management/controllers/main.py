# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) Solvate Informationstechnologie e.U.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp
import openerp.modules.registry
from openerp.tools.translate import _
from openerp import http, tools
from openerp.http import request
from openerp import SUPERUSER_ID

class Home(http.Controller):
    @http.route('/web/graph_data', type='json', auth="public")
    def graph_data(self, redirect=None, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        property_obj = pool['account.asset.asset'];
        proprty_ids = property_obj.search(cr,uid, []);
        duplicate_id = [];
        res = [{'name':'simulation','data':[]},{'name':'revenue','data':[]}];
        category = []
        for proprty in property_obj.browse(cr, uid, proprty_ids, context = context) :
            category.append(proprty.name)
            res[0]['data'].append([proprty.name,proprty.simulation]);
            res[1]['data'].append([proprty.name,proprty.revenue]);
        return [res,category]

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4: