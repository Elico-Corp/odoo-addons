# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp.addons.base_status.base_stage import base_stage


class oe_modules(base_stage, orm.Model):
    _name = 'oe.modules'
    _description = 'OpenERP Module'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    # _track = {
    #     'state': {
    #         'mt_module_spec': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['spec'],
    #         'mt_module_test': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['alpha','beta'],
    #         'mt_module_stabe': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'stable',
    #         'module.message_type': lambda,  #create corresponde type in xml file
    #     },
    # }

    _columns = {
        'name': fields.char(string="Name", size=32),
        'description': fields.text("Description"),
        'server_ids': fields.many2many(
            'server.linux', 'oe_modules_server_maintian_rel',
            'oe_modules_id', 'server_maintian_id', string="Server"),
        'dir_path': fields.char(string="Dir path", size=64),
        'version': fields.char(string="Version", size=12),
        'state': fields.selection(
            [('spec', 'Specfication'), ('alpha', 'Alpha'),
             ('beta', 'Beta'), ('stable', 'Stable')],
            string="Status"),
        'developer_id': fields.many2one('res.partner', string='Developer'),
    }
    _defaults = {
        'state': 'spec',
    }
