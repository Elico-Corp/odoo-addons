# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer


_logger = logging.getLogger(__name__)


"""

Exporters for DNS.

In addition to its export job, an exporter has to:

* check in DNS if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date

"""


class DNSBaseExporter(ExportSynchronizer):

    """ Base exporter for DNS """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(DNSBaseExporter, self).__init__(environment)
        self.binding_id = None
        self.external_id = None

    def _get_openerp_data(self):
        """ Return the raw OpenERP data for ``self.binding_id`` """
        return self.session.browse(self.model._name, self.binding_id)

    def run(self, binding_id, *args, **kwargs):
        """ Run the synchronization

        :param binding_id: identifier of the binding record to export
        """
        self.binding_id = binding_id
        self.binding_record = self._get_openerp_data()

        self.external_id = self.binder.to_backend(self.binding_id)
        result = self._run(*args, **kwargs)

        self.binder.bind(self.external_id, self.binding_id)
        return result

    def _run(self):
        """ Flow of the synchronization, implemented in inherited classes"""
        raise NotImplementedError
