# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.unit.synchronizer import Deleter
from openerp.tools.translate import _
from openerp.addons.connector_dns.connector import get_environment
from openerp.addons.connector.queue.job import job


class DNSDeleter(Deleter):
    """ Base deleter for Dnspod """

    def run(self, binding_id, data):
        """ Run the synchronization, delete the record on Dnspod

        :param magento_id: identifier of the record to delete
        """
        self.backend_adapter.delete(data)
        return _('Record %s deleted on Dnspod') % binding_id


@job
def export_delete_record(session, model_name, backend_id, binding_id, data):
    """ Delete a record on Dnspod """
    env = get_environment(session, model_name, backend_id)
    exporter = env.get_connector_unit(DNSDeleter)
    return exporter.run(binding_id, data)
