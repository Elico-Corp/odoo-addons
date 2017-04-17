# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.event import (on_record_create,
                                            on_record_unlink,
                                            on_record_write)

from .unit.delete_synchronizer import export_delete_record
from .unit.export_synchronizer import export_record

_MODEL_NAMES = ('dns.domain', 'dns.record')
_MODEL_NAMES_RECORD = ('dns.record')


@on_record_create(model_names=_MODEL_NAMES)
def create_domain_all_bindings(session, model_name, record_id, fields=None):
    """ Create a job which export all the bindings of a record."""
    if session.context.get('connector_no_export'):
        return
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    export_record.delay(session, record._model._name, record.id, fields=fields)


@on_record_unlink(model_names=_MODEL_NAMES)
def delete_record(session, model_name, record_id, fields=None):
    """ Create a job which delete all the bindings of a record. """
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    data = {}
    data['format'] = 'json'
    data['login_email'] = record.backend_id.login
    data['login_password'] = record.backend_id.password
    if model_name == 'dns.record':
        data['domain_id'] = record.domain_id.dns_id
        data['record_id'] = record.dns_id
    elif model_name == 'dns.domain':
        data['domain_id'] = record.dns_id
    export_delete_record.delay(session, record._model._name,
                               record.backend_id.id, record.id, data)


@on_record_write(model_names=_MODEL_NAMES_RECORD)
def write_export_all_bindings(session, model_name, record_id, fields=None):
    """ Create a job which export all the bindings of a record."""
    if session.context.get('connector_no_export'):
        return
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    export_record.delay(session, record._model._name, record.id, fields=fields,
                        method='write')
