# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
import os


class Py3oReport(models.TransientModel):
    _inherit = 'py3o.report'
    _description = """ Overwrite the create_single_report method, in order to
                   modify the template file of py3o report with multiple sheets
                   before this template file was used to render with local
                   context """

    @api.multi
    def _create_single_report(self, model_instance, data, save_in_attachment):
        """ This function to modify the template file, then generate our py3o
        report"""
        self._get_parser_context(model_instance, data)
        res = super(Py3oReport, self)._create_single_report(
            model_instance,
            data,
            save_in_attachment)
        return res

    @api.multi
    def _get_template_from_path(self, tmpl_name):
        res = super(Py3oReport, self)._get_template_from_path(
            tmpl_name)
        flbk_filename = None
        if res is None and tmpl_name.startswith('/tmp'):
            flbk_filename = os.path.realpath(tmpl_name)
        if self._is_valid_template_filename(flbk_filename):
            with open(flbk_filename, 'r') as tmpl:
                return tmpl.read()
        return res
