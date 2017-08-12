# -*- coding: utf-8 -*-
from openerp.osv import orm, fields


class oe_modules(orm.Model):
    _name = 'oe.modules'
    _inherit = ['mail.thread']

    _columns = {
        'name': fields.char(string="Name", size=32),
        'description': fields.text("Description"),
        'server_ids': fields.many2many(
            'server.maintian', 'oe_modules_server_maintian_rel',
            'oe_modules_id', 'server_maintian_id', string="Server"),
        'dir_path': fields.char(string="Dir path", size=64),
        'version': fields.char(string="Version", size=12),
        'status': fields.selection(
            [('dev', 'Dev'), ('test', 'Test'), ('installed', 'Installed')],
            string="Status"),
    }
