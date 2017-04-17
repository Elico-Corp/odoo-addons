# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter

_logger = logging.getLogger(__name__)


recorder = {}


def call_to_key(method, arguments):
    """ Used to 'freeze' the method and arguments of a call to DNS
    so they can be hashable; they will be stored in a dict.

    Used in both the recorder and the tests.
    """
    def freeze(arg):
        if isinstance(arg, dict):
            items = dict((key, freeze(value)) for key, value
                         in arg.iteritems())
            return frozenset(items.iteritems())
        elif isinstance(arg, list):
            return tuple([freeze(item) for item in arg])
        else:
            return arg

    new_args = []
    for arg in arguments:
        new_args.append(freeze(arg))
    return (method, tuple(new_args))


def record(method, arguments, result):
    """ Utility function which can be used to record test data
    during synchronisations. Call it from DNSAdapter._call

    Then ``output_recorder`` can be used to write the data recorded
    to a file.
    """
    recorder[call_to_key(method, arguments)] = result


def output_recorder(filename):
    import pprint
    with open(filename, 'w') as f:
        pprint.pprint(recorder, f)
    _logger.debug('recorder written to file %s', filename)


class DNSLocation(object):

    def __init__(self, login, password):
        self.login = login
        self.password = password


class DNSAdapter(CRUDAdapter):
    """ External Records Adapter for DNS """

    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(DNSAdapter, self).__init__(environment)
        self.DNS = DNSLocation(
            self.backend_record.login, self.backend_record.password)

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record """
        raise NotImplementedError

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):
        raise NotImplementedError

    def write(self, data):
        """ Update records on the external system """
        raise NotImplementedError

    def delete(self, data):
        """ Delete a record on the external system """
        raise NotImplementedError

    def _call(self, action, arguments):
        raise NotImplementedError
