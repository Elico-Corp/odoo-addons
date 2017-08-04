# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.connector import Binder
from ..backend import icops


class ICOPSBinder(Binder):
    """ Generic Binder for ICOPS """


@icops
class ICOPSModelBinder(ICOPSBinder):
    """
    Bindings are done directly on the binding model.

    Binding models are models called ``icops.{normal_model}``,
    like ``icops.res.partner`` or ``icops.sale.order``.
    They are ``_inherits`` of the normal models and contains
    the ICOPS ID, the ID of the ICOPS Backend and the additional
    fields belonging to the ICOPS instance.
    """
    _model_name = [
        'icops.sale.order',
        'icops.sale.order.line',
        'icops.purchase.order',
        'icops.purchase.order.line'
    ]

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: if True, returns the openerp_id of the icops_xxxx
        record, else return the id (binding id) of that record
        :return: a record ID, depending on the value of unwrap,
                 or None if the external_id is not mapped
        :rtype: int
        """
        binding_ids = self.session.search(
            self.model._name,
            [('icops_id', '=', external_id),
             ('backend_id', '=', self.backend_record.id)])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        binding_id = binding_ids[0]
        if unwrap:
            return self.session.read(self.model._name,
                                     binding_id,
                                     ['openerp_id'])['openerp_id'][0]
        else:
            return binding_id

    def to_backend(self, binding_id):
        """ Give the external ID for an OpenERP ID

        :param binding_id: OpenERP ID for which we want the external id
        :return: backend identifier of the record
        """
        record = self.session.browse(self.model._name,
                                     binding_id)
        assert record
        res = {}
        for icops in record.icops_ids:
            key = '%s_%s' % (icops.backend_id.id, icops.concept)
            res[key] = {'id': icops.record_id}
        return res

    def bind(self, records, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_ids: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        # avoid to trigger the export when we modify the `icops_id`
        if not records:
            return
        context = self.session.context.copy()
        context['icops'] = True
        now_fmt = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        icops_ids = []
        for record, record_id in records.items():
            backend_id, concept = record.split('_')

            icops_id = (0, 0, {'record_id': record_id['id'],
                        'backend_id': backend_id,
                        'concept': concept,
                        'binding_id': binding_id,
                        'model': record_id['model']})
            icops_ids.append(icops_id)

        self.environment.model.write(
            self.session.cr,
            self.session.uid,
            binding_id,
            {'icops_ids': icops_ids, 'sync_date': now_fmt},
            context=context)
