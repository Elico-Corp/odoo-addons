# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.http import request


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
        cr, _, context = request.cr, request.uid, request.context
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
