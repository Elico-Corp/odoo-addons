# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.addons.connector.unit.mapper import (ExportMapper, ExportMapChild)


class ICOPSExportMapChild(ExportMapChild):
    """ :py:class:`MapChild` for the Exports """

    def _child_mapper(self):
        mapper = self.get_connector_unit_for_model(
            ExportMapper, self.model._name)
        mapper._icops = self._icops
        mapper._backend_to = self._backend_to
        return mapper

    def format_items(self, items_values):
        items = super(ICOPSExportMapChild, self).format_items(items_values)
        return [(5, 0)] + [(0, 0, data) for data in items]


class ICOPSExportMapper(ExportMapper):
    _map_child_class = ICOPSExportMapChild

    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(ICOPSExportMapper, self).__init__(environment)
        self._icops = None
        self._backend_to = None

    def _get_map_child_unit(self, model_name):
        mapper = super(ICOPSExportMapper, self)._get_map_child_unit(model_name)
        mapper._icops = self._icops
        mapper._backend_to = self._backend_to
        return mapper

    def _get_mapping(self, name, record):
        res = {}
        for method in dir(self):
            if method.startswith('%s_' % name):
                new_dict = getattr(self, method)(record)
                res = dict(res.items() + new_dict.items())
        return res
