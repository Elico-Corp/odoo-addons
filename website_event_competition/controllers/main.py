# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Augustin Cisterne-Kaas
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
from openerp import http
from openerp.http import request
# from openerp.tools.translate import _


class EventCompetition(http.Controller):
    fields = ['serial_id', 'name', 'guardian_name', 'phone', 'email',
              'attachment', 'address', 'terms', 'available']

    def _values(self, kwargs):
        values = {}
        for field in self.fields:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        return values

    @http.route('/competition', type='http',
                methods=['GET'], auth="public", website=True)
    def index(self, **kwargs):
        values = self._values(kwargs)
        return request.website.render(
            "website_event_competition.index", values)

    @http.route('/competition', type='http',
                methods=['POST'], auth="public", website=True)
    def post(self, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context
        registration_obj = request.registry['event.registration']
        values = self._values(kwargs)
        registration = None
        try:
            registration = registration_obj.form_create(
                cr, 1, dict(values), context=context)
        except Exception, e:
            values['error'] = str(e).split(',')
            return request.website.render(
                "website_event_competition.index", values)
        values = {'registration': registration}
        return request.website.render(
            "website_event_competition.success", values)
