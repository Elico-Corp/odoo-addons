# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
from lxml import etree
from openerp import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    br_required = fields.Boolean(
        'Business Requirement required',
        help='If marked as true the task linked to the project'
             ' will required business requirement link')

    @api.model
    def fields_view_get(
        self,
        view_id=None,
        view_type='form',
        toolbar=False,
        submenu=False
    ):
        res = super(ProjectTask, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            if 'business_requirement_id' in res['fields'].keys() and (
                self._context.get('search_default_project_id')
            ):
                if self.env['project.project'].browse(
                    self._context.get('search_default_project_id')
                ).project_categ_id.br_required:
                    for node in doc.xpath(
                        "//field[@name='business_requirement_id']"
                    ):
                        node.set("required", "1")
                        modifiers = json.loads(node.get("modifiers"))
                        modifiers['required'] = True
                        node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc)
        return res
