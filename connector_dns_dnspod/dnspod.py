# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import httplib
import json
import urllib

from openerp import api, models
from openerp.addons.connector.unit.mapper import ExportMapper, mapping

from .backend import dnspod
from .unit.backend_adapter import DNSPodAdapter
from .unit.export_synchronizer import DNSExporter


class DNSPodBackend(models.Model):
    _inherit = 'dns.backend'

    def _select_version(self):
        """return version selection"""
        res = []
        res.append(('dnspod', 'dnspod'))
        return res

    @api.multi
    def params(self):
        return {'format': 'json', 'login_email': self.login,
                'login_password': self.password}

    def request(self, action, params, method='POST'):
        """send request to 'dnsapi.cn'"""
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/json"
        }
        conn = httplib.HTTPSConnection("dnsapi.cn")
        conn.request(method, '/' + action, urllib.urlencode(params), headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if response.status == 200:
            return data
        else:
            return None

    @api.one
    def button_connect(self):
        params = self.params()
        data = self.request('Domain.List', params)
        data = json.loads(data)
        if int(data['status']['code']) != -1:
            self.state = 'done'
        else:
            self.state = 'exception'

    @api.one
    def button_set_draft(self):
        self.state = 'draft'


class DNSPodDomain(models.Model):
    _inherit = 'dns.domain'


class DNSPodRecord(models.Model):
    _inherit = 'dns.record'

    def _type_select_version(self):
        res = [('A', '默认'), ('B', '电信'), ('C', '联通'),
               ('D', '教育网'), ('E', '百度'), ('F', '搜索引擎')]
        return res

    def _line_select_version(self):
        res = [('A', 'A'), ('CNAME', 'CNAME'), ('MX', 'MX'),
               ('TXT', 'TXT'), ('NS', 'NS'), ('AAAA', 'AAAA'),
               ('SRV', 'SRV'), ('Visibile URL', '显性URL'),
               ('Invisible URL', '隐现URL')]
        return res


@dnspod
class DNSRecordExport(DNSExporter):
    _model_name = ['dns.record']


@dnspod
class DNSRecordAdapter(DNSPodAdapter):
    _model_name = 'dns.record'
    _dns_model = 'Record'


@dnspod
class DNSRecordExportMapper(ExportMapper):
    _model_name = 'dns.record'
    direct = [('name', 'record')]

    @mapping
    def default(self, record):
        result = {
            'format': 'json',
            'login_email': record.domain_id.backend_id.login,
            'login_password': record.domain_id.backend_id.password,
            'domain_id': record.domain_id.dns_id,
            'sub_domain': record.name,
            'record_line':
            dict(record._fields['type']._column_selection(
                record)).get(record.type),
            'record_type':
            dict(record._fields['line']._column_selection(
                 record)).get(record.line),
            'value': record.value,
            'mx': record.mx_priority,
            'ttl': record.ttl,
        }
        return result


@dnspod
class DNSDomainExport(DNSExporter):
    _model_name = ['dns.domain']


@dnspod
class DNSDomainAdapter(DNSPodAdapter):
    _model_name = 'dns.domain'
    _dns_model = 'Domain'


@dnspod
class DNSDomainExportMapper(ExportMapper):
    _model_name = 'dns.domain'
    direct = [('name', 'domain')]

    @mapping
    def default(self, record):
        return {
            'format': 'json',
            'login_email': record.backend_id.login,
            'login_password': record.backend_id.password
        }
