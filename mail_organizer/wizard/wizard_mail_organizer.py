# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, osv


class wizard_mail_organizer(osv.osv_memory):
    _name = 'wizard.mail.organizer'

    def _select_models(self, cr, uid, context=None):
        module_pool = self.pool.get('ir.model')
        module_ids = module_pool.search(
            cr, uid, [('mail_organizer', '=', True)],
            order="name", context=context)
        modules = module_pool.browse(cr, uid, module_ids, context=context)
        return [(m.model, m.name) for m in modules]

    def _get_default_message_id(self, cr, uid, context=None):
        return context.get('active_id', None)

    _columns = {
        'message_id': fields.many2one(
            'mail.message', string="Message", required=True),
        'res': fields.char('Ressource', readonly=True),
        'model': fields.selection(
            _select_models, string="Model", readonly=True),
        'new_res_id': fields.integer("New resource"),
        'new_model': fields.selection(_select_models, string='New model'),
        'subject': fields.char('Subject', readonly=True),
        'email_from': fields.char('Email'),
        'author_id': fields.many2one(
            'res.partner', string='Author', readonly=True),
        'has_domain': fields.boolean('Filter by partner'),
        'is_domain_visible': fields.boolean('Is domain visible')
    }

    _defaults = {
        'message_id': lambda self, cr, uid, c: (
            self._get_default_message_id(cr, uid, context=c)),
        'has_domain': True,
        'is_domain_visible': False
    }

    def onchange_new_model(self, cr, uid, ids, new_model, has_domain,
                           author_id, context=None):
        res = {}
        vals = {'new_res_id': None}
        domain = {'new_res_id': []}
        if new_model:
            obj_pool = self.pool.get(new_model)
            vals.update({'is_domain_visible': False})
            if 'partner_id' in obj_pool._columns:
                if has_domain:
                    domain = {'new_res_id': [('partner_id', '=', author_id)]}
                vals.update({'is_domain_visible': True})
        res.update({'value': vals, 'domain': domain})
        return res

    def onchange_message_id(self, cr, uid, ids, message_id, context=None):
            res = {}
            if not message_id:
                return res
            vals = {}
            message_pool = self.pool.get('mail.message')
            message = message_pool.browse(
                cr, uid, message_id, context=context)
            resource = ''
            if message.model and message.res_id:
                obj_pool = self.pool.get(message.model)
                obj = obj_pool.browse(
                    cr, uid, message.res_id, context=context)
                resource = getattr(obj, obj._rec_name)
            vals.update({
                'model': message.model,
                'res': resource,
                'email_from': message.email_from,
                'author_id': (message.author_id and message.author_id.id
                              or None),
                'subject': message.subject
            })
            res.update({'value': vals})
            return res

    def confirm(self, cr, uid, ids, context=None):
        message_pool = self.pool.get('mail.message')
        for wz in self.browse(cr, uid, ids, context=context):
            data = {'model': wz.new_model, 'res_id': wz.new_res_id}
            message_pool.write(
                cr, uid, wz.message_id.id, data, context=context)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
