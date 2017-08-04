# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.addons.connector.event import (on_record_write,
                                            on_record_create,
                                            on_record_unlink
                                            )
from .unit.export_synchronizer import (
    export_record)

_MODEL_NAMES = ()
_BIND_MODEL_NAMES = ()
_UNLINK_MODEL_NAMES = ()
_UNLINK_BIND_MODEL_NAMES = ()


@on_record_create(model_names=_BIND_MODEL_NAMES)
@on_record_write(model_names=_BIND_MODEL_NAMES)
def delay_export(session, model_name, record_id, fields=None):
    """ Delay a job which export a binding record.

    (A binding record being a ``icops.res.partner``,
    ``icops.sale.order``, ...)
    """
    export_record(session, model_name, record_id, fields=fields)


@on_record_write(model_names=_MODEL_NAMES)
def delay_export_all_bindings(session, model_name, record_id, fields=None):
    """ Delay a job which export all the bindings of a record.

    In this case, it is called on records of normal models and will delay
    the export for all the bindings.
    """
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    for binding in record.icops_bind_ids:
        export_record(session, binding._model._name, binding.id,
                      fields=fields)


@on_record_unlink(model_names=_UNLINK_MODEL_NAMES)
def delay_unlink(session, model_name, record_id):
    """ Delay a job which delete a record on Magento.

    Called on binding records."""
    fields = {'icops_delete': True}
    delay_export_all_bindings(session, model_name, record_id, fields)


@on_record_unlink(model_names=_UNLINK_BIND_MODEL_NAMES)
def delay_unlink_binding(session, model_name, record_id):
    """ Delay a job which delete a record on Magento.

    Called on binding records."""
    fields = {'icops_delete': True}
    delay_export(session, model_name, record_id, fields)
