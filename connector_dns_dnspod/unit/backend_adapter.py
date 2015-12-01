# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector_dns.unit.backend_adapter import DNSAdapter
import urllib
import httplib
import json


class DNSPodAdapter(DNSAdapter):
    """ External Records Adapter for DNSPod """

    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(DNSAdapter, self).__init__(environment)

    def create(self, data):
        return self._call('%s.Create' % self._dns_model, data)

    def write(self, data):
        """ Update records on the external system """
        return self._call('%s.Modify' % self._dns_model, data)

    def delete(self, data):
        """ Delete a record on the external system """
        return self._call('%s.Remove' % self._dns_model, data)

    def _call(self, action, arguments):
        """Send request to 'dnsapi.cn'"""
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/json"
        }
        try:
            conn = httplib.HTTPSConnection("dnsapi.cn")
            conn.request(
                'POST', '/%s' % action, urllib.urlencode(arguments), headers)
        except:
            raise
        response = conn.getresponse()
        data = response.read()
        conn.close()
        data_json = json.loads(data)
        if 'domain' in data_json:
            data_json['id'] = data_json['domain']['id']
        elif 'record' in data_json:
            data_json['id'] = data_json['record']['id']
        if response.status == 200:
            return data_json
