# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, osv, fields
from openerp.addons.connector.connector import Environment
from openerp.addons.connector.checkpoint import checkpoint


class base_intercompany_installed(orm.AbstractModel):
    """Empty model used to know if the module is installed on the
    database.

    If the model is in the registry, the module is installed.
    """
    _name = 'base_intercompany.installed'


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.browse('icops.backend', backend_id)
    env = Environment(backend_record, session, model_name)
    lang_code = 'en_US'
    env.set_lang(code=lang_code)
    return env


class icops_binding(orm.AbstractModel):
    _name = 'icops.binding'
    _inherit = 'external.binding'
    _description = 'Coswin Binding (abstract)'

    _columns = {
        'backend_id': fields.many2one(
            'icops.backend',
            'ICOPS Backend',
            required=True,
            ondelete='restrict'),
        'icops_ids': fields.one2many(
            'icops.record', 'binding_id',
            string="ICOPS Record"),
    }


class icops_record(orm.Model):
    _name = 'icops.record'

    _columns = {
        'binding_id': fields.integer('ICOPS Binding'),
        'record_id': fields.integer('ICOPS ID'),
        'model': fields.char('Model'),
        'concept': fields.char('Concept'),
        'backend_id': fields.many2one(
            'icops.backend', 'ICOPS Backends'),
    }


class icops_model(orm.AbstractModel):
    _name = 'icops.model'

    def _is_locked(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            pool = self.pool.get('icops.record')
            record_ids = pool.search(
                cr, uid, [('record_id', '=', obj.id),
                          ('model', '=', self._name)])

            res[obj.id] = True if record_ids else False
        return res

    def _check_icops(self, cr, uid, ids, context=None):
        context = context or {}
        if isinstance(ids, int):
            ids = [ids]
        if 'icops' in context:
            return
        fields = ['locked', 'temp_unlock']
        for obj in self.read(cr, uid, ids, fields, context=context):
            if obj['temp_unlock']:
                return
            elif obj['locked']:
                raise osv.except_osv(
                    'ICOPS Error',
                    'This object is locked by an intercompany process')

    _columns = {
        'locked': fields.function(
            _is_locked, type='boolean', string='Is Locked', store=False),
        # To handle special workflow
        'temp_unlock': fields.boolean('Temporary Unlock')
    }

    def action_unlock(self, cr, uid, ids, context):
        pool = self.pool.get('icops.record')
        for obj in self.browse(cr, uid, ids, context=context):
            record_ids = pool.search(
                cr, uid, [('record_id', '=', obj.id),
                          ('model', '=', self._name)])
            pool.unlink(cr, uid, record_ids, context=context)


def add_checkpoint(session, model_name, record_id, backend_id):
    """ Add a row in the model ``connector.checkpoint`` for a record,
    meaning it has to be reviewed by a user.

    :param session: current session
    :type session: :py:class:openerp.addons.connector.session.ConnectorSession
    :param model_name: name of the model of the record to be reviewed
    :type model_name: str
    :param record_id: ID of the record to be reviewed
    :type record_id: int
    :param backend_id: ID of the Coswin Backend
    :type backend_id: int
    """
    return checkpoint.add_checkpoint(session, model_name, record_id,
                                     'icops.backend', backend_id)
