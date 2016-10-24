# -*- coding: utf-8 -*-
from openerp.osv import fields, osv, orm
import paramiko
from openerp.tools.translate import _
import logging
logger = logging.getLogger(__name__)


class server_tags(orm.Model):
    _name = 'server.tags'
    _description = 'Server Tags'

    _columns = {
        'name': fields.char('Name', size=16,
                            required=True),
        'type': fields.char('Type', size=12),
    }

class server_general(orm.Model):
    _name = 'server.general'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Template Server'

    _columns = {
        'name': fields.char('Name', size=128,
                            required=True),
        'type': fields.char('Server Type', size=12),
        'version': fields.char('Version', size=32),
        'public_ip': fields.char('Public IP', size=32),
        'internal_ip': fields.char('Internal IP', size=32),
        'port': fields.char('Port', size=6),
        'path_log': fields.char('Log Path', size=32),
        'path_data': fields.char('Data Path', size=32),
        'path_conf': fields.char('Conf Path', size=32),
        'user_ids': fields.one2many('server.user','server_id',string='Users'),
        'state': fields.selection(
            [('new', 'New'), ('closed', 'Closed'),
             ('run', 'Running'), ('expire', 'Expired')],
            string="States"),
    }


class maintain_disk(orm.Model):
    _name = 'maintain.disk'
    _description = 'Parameters'

    _columns = {
        'name': fields.char('Mount Point', size=64,
                            required=True, translate=True),
    }
    _order = "name"


class maintain_parameter_disk(osv.osv):
    _name = 'maintain.parameter.disk'
    _description = 'Disk Parameters'
    _rec_name = 'parameter'

    _columns = {
        'maintain_id': fields.many2one(
            'server.linux', 'Server Name', required=True),
        'parameter':  fields.many2one(
            'maintain.disk', 'Mount Point', required=True),
        'space': fields.char('Disk Space'),
    }
maintain_parameter_disk()


class maintain_system(osv.osv):
    _name = 'maintain.system'
    _description = 'System Parameters'

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
    }
    _order = "name"

maintain_system()


class maintain_parameter_system(osv.osv):
    _name = 'maintain.parameter.system'
    _description = 'System Parameters'
    _rec_name = 'parameter'

    _columns = {
        'maintain_id': fields.many2one(
            'server.linux', 'Server Name', required=True),
        'parameter':  fields.many2one(
            'maintain.system', 'Name', required=True),
        'source': fields.char('Source'),
        'conf': fields.char('Conf'),
        'log': fields.char('Log'),
    }
maintain_parameter_system()


class erp_parameter(osv.osv):
    _name = 'erp.parameter'
    _description = 'ERP Parameters'

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
    }
    _order = "name"

erp_parameter()


class maintain_erp_parameter(osv.osv):
    _name = 'maintain.erp_parameter'
    _description = 'ERP Parameters'
    _rec_name = 'parameter'

    _columns = {
        'maintain_id': fields.many2one(
            'server.linux', 'Server Name', required=True),
        'parameter':  fields.many2one(
            'erp.parameter', 'Name', required=True),
        'production': fields.char('Production Server'),
        'trunk': fields.char('Trunk Server'),
        'release': fields.char('Release Server'),
    }
maintain_erp_parameter()

class server_user(orm.Model):
    _name = 'server.user'
    _description = 'Server User'
    _rec_name = 'username'

    _columns = {
        'server_id': fields.many2one(
            'server.general', 'Server Name', required=True),
        'username':  fields.char('User Name', size=24, required=True),
        'password': fields.char('Password'),
        'type': fields.selection(
            [('postgres', 'Postgres'), ('openerp', 'OpenERP'),
            ('baazar', 'Baazar'), ('nginx', 'Nginx'),
            ('munin', 'Munin'), ('linux', 'Linux'),
            ],
            string='Type'),

    }

class web_parameter(osv.osv):
    _name = 'web.parameter'
    _description = 'ERP Parameters'

    _columns = {
        'name': fields.char('DB User', size=64, required=True, translate=True),
    }
    _order = "name"

web_parameter()


class maintain_webserver_parameter(osv.osv):
    _name = 'maintain.webserver_parameter'
    _description = 'ERP Parameters'
    _rec_name = 'name'

    _columns = {
        'maintain_id': fields.many2one(
            'server.linux', 'Server Name', required=True),
        'name':  fields.many2one(
            'web.parameter', 'Name', required=True),
        'user': fields.char('User'),
        'version': fields.char('Version'),
        'log_path': fields.char('Log'),
        'error_path': fields.char('Error Path'),
        'domian': fields.char('Domain'),
        'port': fields.char('Port'),

    }
maintain_webserver_parameter()


class ssh_key(osv.osv):
    _name = "ssh.key"

    _columns = {
        'name': fields.char('Name', size=30, required=True, translate=True),
        'id_rsa': fields.text('id_rsa', required=True),
        'id_rsa.pub': fields.text('id_rsa.pub', required=True),
        'active': fields.boolean('Active'),
        'user': fields.many2one('res.partner', 'User', size=30),
        'server_ids': fields.many2many(
            'server.linux', 'server_maintian_ssh_key_rel',
            'ssh_key_id', 'server_maintian_id', string="Severs"),
    }

    _defaults = {
        'active': True,
    }
ssh_key()


class server_linux(orm.Model):
    _name = "server.linux"
    _inherit = ['server.general']
    _description = "Server Linux"

    _columns = {
        'name': fields.char('Machine Name', size=64, required=True),
        'partner_id': fields.many2one(
            'res.partner', 'Customer Name',
            domain=[('is_company', '=', True), ('customer', '=', True)]),
        'responsible_id': fields.many2one('res.partner', 'User'),
        'public_ip': fields.char('Public IP', size=64, ),
        'private_id': fields.char('Private IP', size=64),
        'ubuntu_version': fields.char('Ubuntu Version', size=64,),
        'login': fields.char('Login', size=64,),
        'password': fields.char('Password', size=64,),
        'port': fields.integer('Port'),
        'cpu': fields.char('CPU', size=64,),
        'Memory': fields.char('Total Memory(kb)',),
        'ssh': fields.text('SSH Information',),
        'server_version': fields.selection(
            [('trunk', 'trunk'), ('stable', 'stable'), ('release', 'Release')],
            string='OpenERP Server',),
        'notes': fields.text('Note',),

        'disk_ids': fields.one2many(
            'maintain.parameter.disk', 'maintain_id',
            ondelete='cascade'),
        'system_ids': fields.one2many(
            'maintain.parameter.system', 'maintain_id',
            ondelete='cascade'),
        'erp_ids': fields.one2many(
            'maintain.erp_parameter', 'maintain_id',
            ondelete='cascade'),
        'linux_users': fields.one2many(
            'server.user', 'server_id',
            ondelete='cascade'),
        'pg_servers': fields.one2many(
            'server.postgres', 'server_id',
            ondelete='cascade'),
        'web_ids': fields.one2many(
            'maintain.webserver_parameter', 'maintain_id',
            ondelete='cascade'),
        # 'oe_module_ids': fields.many2many(
        #     'oe.modules', 'oe_modules_server_maintian_rel',
        #     'server_maintian_id', 'oe_modules_id', string="OE Modules"),
        'ssh_key_ids': fields.many2many('ssh.key', string="ssh Keys"),

        'postgres_version': fields.char('Postgres Version', size=64,),
        'postgres_source': fields.char('Source Code Folder', size=64,),
        'postgres_conf': fields.char('Conf Path', size=64,),
        'postgres_port': fields.char('Port', size=64,),
        'linux_user': fields.char('Linux users', size=64,),
        'tools': fields.char('Graphic Tools', size=64,),
        'http': fields.char('Http Server', size=64,),
        'https': fields.char('Https Server', size=64,),
        'ssl': fields.char('SSL Certificates Path', size=64,),
        'https': fields.char('Https Server', size=64,),
        'pg_scripts': fields.char('Scripts File path', size=64,),
        'backup_path': fields.char('PG Backup Dir ', size=64,),
        'backup_log': fields.char('PG Backup Log', size=64,),
        'pg_port': fields.char('PG Port', size=64,),
        'pg_host': fields.char('PG Host', size=64,),
        'pg_user': fields.char('PG User', size=64,),
    }

    def action_connection(self, cr, uid, ids, vals, context=None):
        if not isinstance(ids, list):
            ids = [ids]

        proxy = self.pool['ir.config_parameter']
        ssh_file = proxy.get_param(cr, uid, 'sshkey_path')

        for idc in ids:
            server = self.browse(cr, 1, idc)
            ip = server.public_ip
            port = int(server.port)

            if('server_version' in vals):
                if vals['server_version'] == 'trunk':
                    command = '/etc/init.d/openerp-server_trunk status'
                elif vals['server_version'] == 'stable':
                    command = '/etc/init.d/openerp-server_stable restart'
                elif vals['server_version'] == 'release':
                    command = '/etc/init.d/openerp-server_release restart'
                elif vals['server_version'] == 'posgtres':
                    command = '/etc/init.d/postgresql restart'

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username='root', password='1',
                            port=port, key_filename=ssh_file)
                stdin, stdout, stderr = ssh.exec_command(command)
                result = stdout.readlines()
                ssh.close()
                raise osv.except_osv(_('Result'), _(result))


class server_postgres(orm.Model):
    _name = 'server.postgres'
    _inherit = ['server.general']
    _description = 'Postgres Server'

    _columns = {
        'type': fields.char('Type', size=12),
        'server_id': fields.many2one('server.linux', 'Linux Server'),
        'public_ip': fields.related('server_id','public_ip', type='char', string='Server IP'),
    }
    _defaults = {
        'type': 'postgres',
        'state': 'new',
    }
