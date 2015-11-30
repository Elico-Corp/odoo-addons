# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class DNSBackend(models.Model):
    _name = 'dns.backend'
    _inherit = 'connector.backend'
    _backend_type = 'dns'

    def _select_version(self):
        return []

    login = fields.Char('Login', help="Provider's login.", required=True)
    password = fields.Char('Password', help="Provider's password.",
                           required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done'),
         ('exception', 'Exception')], 'State', default="draft",
        help='"Confirmed" when the domain has been succesfully created.')
    version = fields.Selection(
        '_select_version', string='Service Provider',
        help='DNS service provider',
        required=True)

    @api.multi
    def name_get(self):
        res = []
        for backend in self:
            res.append((backend.id, '%s (%s)' % (backend.name, backend.login)))
        return res


class DNSDomain(models.Model):
    _name = 'dns.domain'
    _inherit = 'dns.binding'

    name = fields.Char('Name', required=True,
                       help='Domain name without "www",such as"dnspod.cn"')
    record_ids = fields.One2many('dns.record', 'domain_id',
                                 String='Subdomains')


class DNSRecord(models.Model):
    _name = 'dns.record'
    _inherit = 'dns.binding'

    def _line_select_version(self):
        return []

    def _type_select_version(self):
        return []

    name = fields.Char('Sub domain', help="host record,such as 'www'",
                       required=True)
    domain_id = fields.Many2one(
        'dns.domain', string="Domain", domain="[('state','=','done')]",
        ondelete='cascade', help="Domain which has already confirmed")
    type = fields.Selection('_type_select_version', string='Record Type')
    line = fields.Selection('_line_select_version', string='Record Line')
    value = fields.Text('Value', help="such as IP:200.200.200.200",
                        required=True)
    mx_priority = fields.Integer(string='MX priority', help="scope:1-20",
                                 default=1)
    ttl = fields.Integer('TTL', default=600, help="scope:1-604800",
                         required=True)
    backend_id = fields.Many2one('dns.backend', related='domain_id.backend_id',
                                 store=True)
