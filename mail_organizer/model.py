# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, orm


class ir_model(orm.Model):
    _inherit = 'ir.model'
    _columns = {
        'mail_organizer': fields.boolean('Use in Mail Organizer')
    }
