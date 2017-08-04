# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, orm


class mail_message(orm.Model):
    _inherit = 'mail.message'
    _columns = {
        'name': fields.char('Name')
    }
